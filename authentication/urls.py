# Third Party
from django.urls import path

# Authentication
from authentication.views import AmazonLogin, AmazonCallback

urlpatterns = [
    path("oauth/amazon/login/", AmazonLogin.as_view(), name="amazon_login"),
    path("oauth/amazon/callback/", AmazonCallback.as_view(), name="amazon_callback"),
]
