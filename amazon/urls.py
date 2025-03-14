from django.urls import path
from amazon.views import TryApi, FetchSellerCentralDataAPI, SalesAPI, GetRegionsAPI

urlpatterns = [
    path("tryApi/", TryApi.as_view(), name="try-api"),
    path("fetchData/", FetchSellerCentralDataAPI.as_view(), name="fetch-data"),
    path("getSalesReport/", SalesAPI.as_view(), name="get-sales-report"),
    path("getRegions/", GetRegionsAPI.as_view(), name="get-regions"),
]
