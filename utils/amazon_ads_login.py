# Standard Packages
from typing import Dict
from urllib.parse import urlencode, urljoin

# Third Party
import requests
from django.conf import settings


from utils.constants import AMAZON_ADS_LOGIN_BASE_URL, AMAZON_ADS_TOKEN_BASE_URL


class AmazonAdsLogin:
    def __init__(self):
        self.config = settings.AMAZON_ADS_CONFIG
        self.client_id = self.config["AMAZON_ADS_CLIENT_ID"]
        self.client_secret = self.config["AMAZON_ADS_CLIENT_SECRET"]
        self.redirect_uri = self.config["AMAZON_ADS_REDIRECT_URI"]
        self.scope = self.config["AMAZON_ADS_SCOPE"]

    def _get_query_params(self, scope: str):
        return {
            "client_id": self.client_id,
            "scope": scope,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
        }

    def _get_data_for_token(self, code: str) -> Dict:
        return {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

    def generate_login_url(self, region: str) -> str:
        base_url = AMAZON_ADS_LOGIN_BASE_URL[region]
        query_params = self._get_query_params(scope=self.scope)
        query_string = urlencode(query_params)
        url = urljoin(base_url, "?" + query_string)
        return url

    def generate_access_and_refresh_tokens(self, code: str, region: str) -> Dict:
        url = AMAZON_ADS_TOKEN_BASE_URL[region]
        data = self._get_data_for_token(code=code)
        response = requests.post(url, data=data)
        return response.json()

    def generate_access_token_using_refresh_token(self, refresh_token: str, region: str) -> Dict:
        url = AMAZON_ADS_TOKEN_BASE_URL[region]
        data = {
            "grant_type": "refresh_token",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
        }
        response = requests.post(url, data=data)
        return response.json()


amazon_ads_login = AmazonAdsLogin()
