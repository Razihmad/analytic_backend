from django.urls import path
from amazon.views import (
    TryApi,
    FetchSellerCentralDataAPI,
    SalesAPI,
    GetRegionsAPI,
    FetchSalesReportByDate,
    GetAmazonProfileData,
)

urlpatterns = [
    path("tryApi/", TryApi.as_view(), name="try-api"),
    path("fetchData/", FetchSellerCentralDataAPI.as_view(), name="fetch-data"),
    path("getSalesReport/", SalesAPI.as_view(), name="get-sales-report"),
    path("getRegions/", GetRegionsAPI.as_view(), name="get-regions"),
    path("fetchDataByDate/", FetchSalesReportByDate.as_view(), name="fetch-by-date"),
    path("getProfileData/", GetAmazonProfileData.as_view(), name="get-profile-data"),
]
