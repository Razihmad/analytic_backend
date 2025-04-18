from django.urls import path

from amazon_ads.views import FetchAdsReportByDate, GetCampaignReport, UploadCampaignReportFile

urlpatterns = [
    path("fetchAdsDataByDate/", FetchAdsReportByDate.as_view(), name="fetch-ads-data-by-date"),
    path("uploadFile/", UploadCampaignReportFile.as_view(), name="upload-sb-report-file"),
    path("getCampginReportData/", GetCampaignReport.as_view(), name="get-campaign-report-data"),
]
