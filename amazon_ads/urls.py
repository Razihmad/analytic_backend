from django.urls import path

from amazon_ads.views import FetchAdsReportByDate

urlpatterns = [
    path("fetchAdsDataByDate/", FetchAdsReportByDate.as_view(), name="fetch-ads-data-by-date")
]
