import logging
import requests
from typing import Optional, Tuple

from django.conf import settings
from sp_api.base import Marketplaces
from base.exception import ServiceException
from utils.constants import BaseEndpoint
from project.constants import Environment

logger = logging.getLogger(__name__)


class LoginWithAmazon:
    def __init__(self):
        self.config = settings.AMAZON_CONFIG
        self.client_id = self.config["AMAZON_CLIENT_ID"]
        self.client_secret = self.config["AMAZON_CLIENT_SECRET"]
        self.app_id = self.config["AMAZON_APP_ID"]
        self.token_base_url = self.config["AMAZON_TOKEN_BASE_URL"]
        self.environment = settings.ENVIRONMENT

    def generate_login_url(self, country: str, country_code: str) -> Tuple[str, str]:
        marketplace_data = getattr(BaseEndpoint, country.upper())
        marketplace = getattr(Marketplaces, country_code.upper())
        marketplace_id = marketplace.marketplace_id
        base_url = marketplace_data.value
        query_params = {
            "application_id": self.app_id,
            "state": marketplace_id
        }
        logger.info(f"query_params: {country=}, {country_code=}, {query_params=}, {base_url=}, {self.environment=}")
        if self.environment != Environment.PRODUCTION.value:
            query_params["version"] = "beta"
        path = "/apps/authorize/consent"
        from urllib.parse import urlencode, urljoin
        query_string = urlencode(query_params)
        url = urljoin(base_url, path + "?" + query_string)
        return url, marketplace_id

    def url_for_access_and_refresh_token(self, code: Optional[str] = None, refresh_token: Optional[str] = None) -> str:
        logger.info(f"{code=}, {refresh_token=}, {self.token_base_url=}")
        if code:
            return f"{self.token_base_url}?grant_type=authorization_code&code={code}&client_id={self.client_id}&client_secret={self.client_secret}"
        elif refresh_token:
            return f"{self.token_base_url}?grant_type=refresh_token&refresh_token={refresh_token}&client_id={self.client_id}&client_secret={self.client_secret}"

    def generate_refresh_token(self, code: str):
        url = self.url_for_access_and_refresh_token(code=code)
        response = requests.post(url)
        if response.status_code != 200:
            logger.error("error", response.text)
            raise ServiceException("Error while generating refresh token")

        return response.json()

    def generate_access_token(self, refresh_token: str):
        url = self.url_for_access_and_refresh_token(refresh_token=refresh_token)
        response = requests.post(url)
        if response.status_code != 200:
            logger.error(f"error {response.text}", exc_info=True)
            raise ServiceException("Error while generating access token")

        return response.json()


amazon_login = LoginWithAmazon()
