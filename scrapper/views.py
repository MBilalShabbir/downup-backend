from rest_framework import generics, status, mixins
from rest_framework.response import Response
import time
import requests
import asyncio
from scrapper.utils.scrapping_utils import bs_images, scrape_images_and_routes, get_images_async


def get_domain_from_url(url):
    if url:
        url = url.split("//")[-1].split("/")[0].split('?')[0].replace('www.', '').replace('Www.', '').replace(' ', '')
    return url


class ScrapSite(generics.GenericAPIView):
    def post(self, request):
        bs_images.clear()
        req_data = request.data
        url = req_data.get('url')

        domain = get_domain_from_url(url)
        url = f"http://{domain}"

        all_images, all_urls, logo_url = scrape_images_and_routes(url, domain)
        asyncio.run(get_images_async(all_urls))
        for image in all_images:
            bs_images.add(image)

        return Response({
            "logo": logo_url,
            "all_routes": all_urls,
            "images": list(bs_images)
        })
