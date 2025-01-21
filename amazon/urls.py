from django.urls import path
from amazon.views import TryApi
urlpatterns = [
    path("tryApi/", TryApi.as_view(), name="try-api"),
]
