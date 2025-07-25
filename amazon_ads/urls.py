from django.urls import path

from amazon_ads.views import (
    CreateKeyword,
    FetchAdsReportByDate,
    GetCampaignReport,
    TestAccount,
    UploadCampaignReportFile,
    GetSearchTermReportData,
    NegativeKeyword,
    NegativeProductTargeting,
    GetTargetingReportData,
)

urlpatterns = [
    path("fetchAdsDataByDate/", FetchAdsReportByDate.as_view(), name="fetch-ads-data-by-date"),
    path("uploadFile/", UploadCampaignReportFile.as_view(), name="upload-sb-report-file"),
    path("getCampginReportData/", GetCampaignReport.as_view(), name="get-campaign-report-data"),
    path("getSearchTermReportData/", GetSearchTermReportData.as_view(), name="get-search-term-report-data"),
    path("testAccount/", TestAccount.as_view(), name="test-account"),
    path("negativeKeyword/", NegativeKeyword.as_view(), name="negative-keyword"),
    path("createKeyword/", CreateKeyword.as_view(), name="create-keyword"),
    path("negativeProductTargeting/", NegativeProductTargeting.as_view(), name="negative-product-targeting"),
    path("getTargetingReportData/", GetTargetingReportData.as_view(), name="get-targeting-report-data"),
]
