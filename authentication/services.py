from typing import Dict, Optional
from authentication.selectors import get_or_create_user
from base.exception import ServiceException
from utils.amazon_login import amazon_login
from utils.google_authetication import google_oauth


from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken


def get_amazon_login_uri(*, marketplace: str):
    return amazon_login.generate_login_url(marketplace=marketplace)


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
