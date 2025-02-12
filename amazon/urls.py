from django.urls import path
from amazon.views import TryApi, FetchSellerCentralDataAPI

urlpatterns = [
    path("tryApi/", TryApi.as_view(), name="try-api"),
    path("fetchData/", FetchSellerCentralDataAPI.as_view(), name="fetch-data"),
]
