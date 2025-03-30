import logging

from typing import Dict, Optional, Tuple
from amazon.models import Seller
from amazon.selectors import get_amazon_accounts_by_user_id, get_seller_by_user_id
from amazon_ads.selectors import get_ads_profile_by_user_and_seller_id
from authentication.selectors import bulk_create_profiles, get_or_create_seller, get_or_create_user
from base.decorators import cache_function
from base.exception import ServiceException
from authentication.utils.amazon_login import amazon_login
from authentication.utils.google_authentication import google_oauth
from authentication.utils.amazon_ads_login import amazon_ads_login
from amazon_ads.utils.amazon_ads_api import amazon_ads_api

from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from sp_api.base import Marketplaces
from typing import List

logger = logging.getLogger(__name__)


def get_amazon_login_uri(*, country: str, country_code: str):

    return amazon_login.generate_login_url(country=country, country_code=country_code)


def get_refresh_token(*, code: str):
    return amazon_login.generate_refresh_token(code=code)


def generate_google_login_url():
    return google_oauth.create_google_login_url()


def create_user_by_google_data(*, data: Dict) -> Tuple[User, bool]:
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
    logger.info(f"{partner_id=}, {refresh_token=}, {marketplace_id=}")
    return get_or_create_seller(partner_id=partner_id, refresh_token=refresh_token, marketplace_id=marketplace_id, user=user)


@cache_function(cache_config_key="SC_ACCESS_TOKEN")
def get_access_token(*, user_id: int , amazon_seller_id: str) -> str:
    refresh_token = get_and_set_refresh_token(user_id=user_id, amazon_seller_id=amazon_seller_id)
    response = amazon_login.generate_access_token(refresh_token=refresh_token)
    access_token = response["access_token"]
    return access_token


@cache_function(cache_config_key="SC_REFRESH_TOKEN")
def get_and_set_refresh_token(*, user_id: int, amazon_seller_id: str) -> str:
    seller = get_seller_by_user_id(user_id=user_id, amazon_seller_id=amazon_seller_id)
    return seller.refresh_token


def get_amazon_ads_login_uri(*, country_code: str) -> Tuple[str, str]:
    marketplace = getattr(Marketplaces, country_code.upper())
    region = marketplace.region
    url = amazon_ads_login.generate_login_url(region=region)
    return url, region


def get_access_and_refresh_token_for_ads(*, code: str, region: str) -> Dict:
    response = amazon_ads_login.generate_access_and_refresh_tokens(code=code, region=region)
    return response


def get_amazon_ads_profie_data(*, region: str, access_token: str) -> List[Dict]:
    return amazon_ads_api.get_ads_profile(access_token=access_token, region=region)


def generate_token_and_get_ads_profile_data(*, code: str, region: str) -> Tuple[str, List[Dict]]:
    response = get_access_and_refresh_token_for_ads(code=code, region=region)
    access_token = response["access_token"]
    refresh_token = response["refresh_token"]
    ads_profiles = get_amazon_ads_profie_data(region=region, access_token=access_token)
    return refresh_token, ads_profiles


def bulk_create_ads_profile(*, profiles: List[Dict]):
    data = []
    for profile in profiles:
        data.append(
            Seller(
                user_id=profile["user_id"],
                store_name=profile["store_name"],
                ads_refresh_token=profile["refresh_token"],
                marketplace_id=profile["marketplace_id"],
                amazon_seller_id=profile["amazon_seller_id"],
                profile_id=profile["profile_id"],
                country_code=profile["country_code"]
            )
        )

    bulk_create_profiles(data=data, update_fields=["ads_refresh_token", "profile_id", "store_name", "country_code"])


@cache_function(cache_config_key="ADS_ACCESS_TOKEN")
def get_ads_access_token(*, user_id: int, amazon_seller_id: str, region: str) -> str:
    refresh_token = get_ads_refresh_token(user_id=user_id, amazon_seller_id=amazon_seller_id)
    tokens = amazon_ads_login.generate_access_token_using_refresh_token(
        refresh_token=refresh_token, region=region
    )
    return tokens["access_token"]


@cache_function(cache_config_key="ADS_REFRESH_TOKEN")
def get_ads_refresh_token(*, user_id: int, amazon_seller_id: str) -> str:
    profile = get_ads_profile_by_user_and_seller_id(user_id=user_id, amazon_seller_id=amazon_seller_id)
    if not profile:
        raise ServiceException("No profile found")
    return profile.ads_refresh_token


@cache_function(cache_config_key="ADS_PROFILE_ID")
def get_ads_profile_id(*, user_id: int, amazon_seller_id: str) -> str:
    profile = get_ads_profile_by_user_and_seller_id(user_id=user_id, amazon_seller_id=amazon_seller_id)
    if not profile:
        raise ServiceException("No profile found")
    return profile.profile_id


def is_seller_and_ads_account_exist(*, user: User) -> bool:
    amazon_accounts = get_amazon_accounts_by_user_id(user_id=user.id)
    amazon_account = amazon_accounts.first()
    if not amazon_account:
        return False, False
    if amazon_account and amazon_account.ads_refresh_token:
        return True, True
    if amazon_account and not amazon_account.ads_refresh_token:
        return True, False
    return False, False
