from typing import Dict, Optional
from amazon.selectors import get_seller_by_user_id
from authentication.selectors import get_or_create_seller, get_or_create_user
from base.decorators import cache_function
from base.exception import ServiceException
from utils.amazon_login import amazon_login
from utils.google_authetication import google_oauth


from django.core.cache import cache
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken


def get_amazon_login_uri(*, country: str, country_code: str):

    return amazon_login.generate_login_url(country=country, country_code=country_code)


def get_refresh_token(*, code: str):
    return amazon_login.generate_refresh_token(code=code)


def generate_google_login_url():
    return google_oauth.create_google_login_url()


def create_user_by_google_data(*, data: Dict) -> User:
    email = data.pop("email", None)
    if not email:
        raise ServiceException("No email exists")
    user_data = {"first_name": data.pop("given_name", None), "last_name": data.pop("family_name", None)}
    user, is_created = get_or_create_user(email=email, extra_data=user_data)
    if is_created:
        return user, True
    if not user.is_active:
        raise ServiceException("User is blocked or deleted")

    return user, is_created


def get_jwt_access_token(*, user: User) -> str:
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)


def get_user_data_from_google_code(*, code: Optional[str]) -> Dict:
    if not code:
        raise ServiceException('No code provided.')

    access_token = google_oauth.google_get_access_token(code=code)
    if not access_token:
        raise ServiceException('Failed to obtain access token from Google.')

    user_data = google_oauth.google_get_user_info(access_token=access_token)

    return user_data


def create_amazon_seller(*, partner_id: str, refresh_token: str, marketplace_id: str, user: User, access_token: str):
    return get_or_create_seller(partner_id=partner_id, refresh_token=refresh_token, marketplace_id=marketplace_id, user=user, access_token=access_token)


def set_cache_for_refresh_and_access_token(*, refresh_token: str, access_token: str, user_id: int):
    cache.set(f"sc_access_token_{user_id}", access_token, timeout=3600)
    cache.set(f"sc_refresh_token_{user_id}", refresh_token, timeout=24 * 60 * 60)


@cache_function(cache_config_key="SC_ACCESS_TOKEN")
def get_access_token(*, user_id: int) -> str:
    refresh_token = get_and_set_refresh_token(user_id=user_id)
    response = amazon_login.generate_access_token(refresh_token=refresh_token)
    access_token = response["access_token"]
    return access_token


@cache_function(cache_config_key="SC_REFRESH_TOKEN")
def get_and_set_refresh_token(*, user_id: int) -> str:
    seller = get_seller_by_user_id(user_id=user_id)
    return seller.refresh_token
