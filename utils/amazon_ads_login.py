# Standard Packages
from urllib.parse import urlencode, urljoin

# Third Party
from django.conf import settings
from utils.constants import AMAZON_ADS_LOGIN_BASE_URL


class AmazonAdsLogin:
    def __init__(self):
        self.config = settings.AMAZON_ADS_CONFIG
        self.client_id = self.config["AMAZON_ADS_CLIENT_ID"]
        self.client_secret = self.config["AMAZON_ADS_CLIENT_SECRET"]
        self.redirect_uri = self.config["AMAZON_ADS_REDIRECT_URI"]

    def _get_query_params(self, scope: str):
        return {
            "client_id": self.client_id,
            "scope": scope,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
        }

    def generate_login_url(self, scope: str, region: str) -> str:
        base_url = AMAZON_ADS_LOGIN_BASE_URL[region]
        query_params = self._get_query_params(scope=scope)
        query_string = urlencode(query_params)
        url = urljoin(base_url, "?" + query_string)
        return url
