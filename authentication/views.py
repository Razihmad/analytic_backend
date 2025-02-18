# Third Party
from django.shortcuts import redirect
from rest_framework.views import APIView
# from rest_framework_simplejwt.authentication import JWTAuthentication
# from rest_framework.permissions import IsAuthenticated

# Base Package
from base.response import status_200

# Authentication
from authentication.services import (
    create_amazon_seller,
    create_user_by_google_data,
    generate_google_login_url,
    get_amazon_ads_login_uri,
    get_amazon_login_uri,
    get_jwt_access_token,
    get_refresh_token,
    get_user_data_from_google_code,
)


# Create your views here.
class AmazonLogin(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        country = request.GET.get("country", "India")
        country_code = request.GET.get("country_code", "IN")
        url = get_amazon_login_uri(country=country, country_code=country_code)
        return redirect(url)


class AmazonCallback(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request):
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
            data={"state": marketplace_id, "spapi_code": spapi_oauth_code, "partner_id": selling_partner_id, "response": response, "seller_data": seller}
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
    def get(self, request, *args, **kwargs):
        code = request.GET.get("code", None)
        user_data = get_user_data_from_google_code(code=code)
        user, is_created = create_user_by_google_data(data=user_data)
        access_token = get_jwt_access_token(user=user)
        return status_200(message="Login successful", data={"is_new_user": is_created, "access_token": access_token})


class AmazonAdsLogin(APIView):
    def get(self, request, *args, **kwargs):
        country = request.GET.get("country", "India")
        country_code = request.GET.get("country_code", "IN")
        url = get_amazon_ads_login_uri(country=country, country_code=country_code)
        return redirect(url)


class AmazonAdsCallback(APIView):
    def get(self, request, *args, **kwargs):
        pass
