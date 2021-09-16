from django.urls import path
from .views import ScrapSite

urlpatterns = [
    path("", ScrapSite.as_view(), name='scrapping'),
]