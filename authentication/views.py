# Third Party
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

# Base Package
from authentication.serializers import serialized_ads_profile_data
from base.decorators import handle_exception
from base.response import status_200

# Authentication
from authentication.services import (
    bulk_create_ads_profile,
    create_amazon_seller,
    create_user_by_google_data,
    generate_google_login_url,
    generate_token_and_get_ads_profile_data,
    get_amazon_ads_login_uri,
    get_amazon_login_uri,
    get_jwt_access_token,
    get_refresh_token,
    get_user_data_from_google_code,
)


# Create your views here.
class AmazonLogin(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @handle_exception
    def post(self, request):
        country = request.GET.get("country", "India")
        country_code = request.GET.get("country_code", "IN")
        url = get_amazon_login_uri(country=country, country_code=country_code)
        return redirect(url)


class AmazonCallback(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @handle_exception
    def post(self, request):
        selling_partner_id = request.GET.get("selling_partner_id")
        spapi_oauth_code = request.GET.get("spapi_oauth_code")
        marketplace_id = request.GET.get("state")
        response = get_refresh_token(code=spapi_oauth_code)
        seller = create_amazon_seller(
            partner_id=selling_partner_id,
            refresh_token=response["refresh_token"],
            marketplace_id=marketplace_id,
            access_token=response["access_token"],
            user=request.user
        )

        return status_200(
            message="Login successful",
            data={
                "state": marketplace_id,
                "spapi_code": spapi_oauth_code,
                "partner_id": selling_partner_id,
                "response": response,
                "seller_data": seller,
            }
        )


class GoogleLogin(APIView):

    def get(self, request, *args, **kwargs):
        login_url = generate_google_login_url()
        # return redirect(login_url)
        return status_200(message="Login successful", data={"login_url": login_url})

    def post(self, request, *args, **kwargs):
        code = request.GET.get("code", None)
        user_data = get_user_data_from_google_code(code=code)
        user, is_created = create_user_by_google_data(data=user_data)
        access_token = get_jwt_access_token(user=user)
        return status_200(message="Login successful", data={"is_new_user": is_created, "access_token": access_token})


class GoogleLoginCallback(APIView):
    def post(self, request, *args, **kwargs):
        code = request.GET.get("code", None)
        user_data = get_user_data_from_google_code(code=code)
        user, is_created = create_user_by_google_data(data=user_data)
        access_token = get_jwt_access_token(user=user)
        return status_200(message="Login successful", data={"is_new_user": is_created, "access_token": access_token})


class AmazonAdsLogin(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        country_code = request.GET.get("country_code", "IN")
        url, region = get_amazon_ads_login_uri(country_code=country_code)
        request.session["region"] = region
        return status_200(message="success", data={"url": url})


class AmazonAdsCallback(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        code = request.GET.get("code")
        region = request.session["region"]
        refresh_token, profiles = generate_token_and_get_ads_profile_data(code=code, region=region)
        serailzed_profiles = serialized_ads_profile_data(profiles=profiles, user_id=request.user.id, refresh_token=refresh_token)
        bulk_create_ads_profile(profiles=serailzed_profiles)
        return status_200(message="success", data={"is_created": True, "start_fetching_data": True})
