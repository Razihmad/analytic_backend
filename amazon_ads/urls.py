from django.urls import path

from amazon_ads.views import FetchAdsReportByDate, UploadCampaignReportFile

urlpatterns = [
    path("fetchAdsDataByDate/", FetchAdsReportByDate.as_view(), name="fetch-ads-data-by-date"),
    path("uploadFile/", UploadCampaignReportFile.as_view(), name="upload-sb-report-file"),
]
