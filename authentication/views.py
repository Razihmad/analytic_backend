import logging

# Third Party
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

# Base Package
from authentication.serializers import serialize_seller, serialized_ads_profile_data
from base.decorators import handle_exception
from base.exception import ServiceException
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
    is_seller_and_ads_account_exist,
)


logger = logging.getLogger(__name__)


# Create your views here.
class AmazonLogin(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @handle_exception
    def post(self, request):
        country = request.GET.get("country", "India")
        country_code = request.GET.get("country_code", "IN")
        logger.info(f"country: {country}, country_code: {country_code}")
        url, marketplace_id = get_amazon_login_uri(country=country, country_code=country_code)
        request.session["state"] = marketplace_id
        request.session["country_code"] = country_code
        return status_200(message="Login successful", data={"url": url})


class AmazonCallback(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @handle_exception
    def post(self, request):
        selling_partner_id = request.data.get("selling_partner_id")
        spapi_oauth_code = request.data.get("spapi_oauth_code")
        marketplace_id = request.data.get("state")
        state = request.session["state"]
        country_code = request.session["country_code"]
        logger.info(f"{selling_partner_id=}, {spapi_oauth_code=}, {state=}, {marketplace_id=}")
        if state != marketplace_id:
            raise ServiceException("Invalid state")
        response = get_refresh_token(code=spapi_oauth_code)
        seller = create_amazon_seller(
            partner_id=selling_partner_id,
            refresh_token=response["refresh_token"],
            marketplace_id=marketplace_id,
            user=request.user,
            country_code=country_code,
        )

        return status_200(
            message="Login successful",
            data={
                "amazon_seller_id": selling_partner_id,
                "seller_data": serialize_seller(seller=seller),
            }
        )


class GoogleLogin(APIView):

    def get(self, request, *args, **kwargs):
        login_url = generate_google_login_url()
        # return redirect(login_url)
        return status_200(message="Login successful", data={"url": login_url})

    def post(self, request, *args, **kwargs):
        code = request.GET.get("code", None)
        user_data = get_user_data_from_google_code(code=code)
        user, is_created = create_user_by_google_data(data=user_data)
        access_token = get_jwt_access_token(user=user)
        return status_200(message="Login successful", data={"is_new_user": is_created, "access_token": access_token})


class GoogleLoginCallback(APIView):

    @handle_exception
    def post(self, request, *args, **kwargs):
        code = request.data.get("code", None)
        user_data = get_user_data_from_google_code(code=code)
        user, is_created = create_user_by_google_data(data=user_data)
        is_seller_exist, is_ads_acc_exist = is_seller_and_ads_account_exist(user=user)
        logger.info(f"Is seller exist: {is_seller_exist=}, {is_ads_acc_exist=}")
        access_token = get_jwt_access_token(user=user)
        return status_200(
            message="Login successful",
            data={
                "is_new_user": is_created or (not is_seller_exist or not is_ads_acc_exist), "access_token": access_token
            }
        )


class AmazonAdsLogin(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @handle_exception
    def post(self, request):
        country_code = request.data.get("country_code", "IN")
        url, region = get_amazon_ads_login_uri(country_code=country_code)
        request.session["region"] = region
        request.session["ad_country_code"] = country_code
        return status_200(message="Login successful", data={"url": url})


class AmazonAdsCallback(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @handle_exception
    def post(self, request, *args, **kwargs):
        code = request.data.get("code")
        region = request.session["region"]
        country_code = request.session["ad_country_code"]
        refresh_token, profiles = generate_token_and_get_ads_profile_data(code=code, region=region)
        serailzed_profiles = serialized_ads_profile_data(profiles=profiles, user_id=request.user.id, refresh_token=refresh_token, country_code=country_code)
        bulk_create_ads_profile(profiles=serailzed_profiles)
        return status_200(message="success", data={"is_created": True, "start_fetching_data": True})
