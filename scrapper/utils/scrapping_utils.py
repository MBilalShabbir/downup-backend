from bs4 import BeautifulSoup
from simplified_scrapy.simplified_doc import SimplifiedDoc
import aiohttp
import requests
import asyncio

DEFAULT_HEADERS = {
    'Accept-Encoding': 'identity',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 '
                  'Safari/537.36',
    'referer': 'https://...'
}

bs_images = set()


def scrape_images_and_routes(url, domain):
    try:
        source_code = requests.get(url, timeout=15, headers=DEFAULT_HEADERS)
    except Exception as e:
        print(str(e))
        return [], [], None
    doc = SimplifiedDoc(source_code.content.decode('utf-8'))  # incoming HTML string
    lst = doc.listA(url=url)  # get all links
    images = doc.listImg(url=url)
    image_urls = set()
    urls = set()
    for a in lst:
        if domain in a['url']:  # sub domains
            urls.add(a['url'].split('?')[0].strip('/'))
            try:
                source_code2 = requests.get(a['url'] + "/", timeout=15, headers=DEFAULT_HEADERS)

                doc2 = SimplifiedDoc(source_code2.content.decode('utf-8'))
                l2 = doc2.listA(url=a['url'] + "/")
                images.extend(doc2.listImg(url=a['url'] + "/"))
                for link in l2:
                    if domain in link['url']:
                        urls.add(link['url'].split('?')[0].strip('/'))
            except Exception as e:
                print(f"error getting images from url {a['url']}: {e}")

    for image in images:
        image_urls.add(image['url'])
    logo_src = None
    soup = BeautifulSoup(source_code.content)
    content_to_find_logo = soup.find('header') or soup.find('footer')
    image = content_to_find_logo.find('img') if content_to_find_logo else None
    if image:
        logo_src = image.get("src") or image.get('data-src')
    return list(image_urls), list(urls), logo_src


async def get_req_response(url, session):
    try:
        async with session.get(url=url) as response:
            resp = await response.read()
            print("Successfully got url {} with resp of length {}.".format(url, len(resp)))
            soup = BeautifulSoup(resp)
            for img in soup.findAll('img'):
                image_url = img.get("src") or img.get('data-src')
                if image_url:
                    bs_images.add(image_url)
    except Exception as e:
        print("Unable to get url {} due to {}.".format(url, e.__class__))


async def get_images_async(urls):
    async with aiohttp.ClientSession() as session:
        ret = await asyncio.gather(*[get_req_response(url, session) for url in urls])
    print("Finalized all. Return is a list of len {} outputs.".format(len(ret)))
