# Third Party
from django.urls import path

# Authentication
from authentication.views import AmazonLogin, AmazonCallback, GoogleLogin, GoogleLoginCallback

urlpatterns = [
    ## authorize amazon seller central
    path("oauth/amazon/login/", AmazonLogin.as_view(), name="amazon_login"),
    path("oauth/amazon/callback/", AmazonCallback.as_view(), name="amazon_callback"),

    ## authorize login with google
    path("oauth/google/login/", GoogleLogin.as_view(), name="google_login"),
    path("oauth/google/login/callback", GoogleLoginCallback.as_view(), name="google_login_callback"),


]
