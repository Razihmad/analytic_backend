import requests
from django.conf import settings

from utils.constants import AMAZON_ADS_API_BASE_ENDPOINT


class AmazonAds:
    def __init__(self):
        self.config = settings.AMAZON_ADS_CONFIG
        self.client_id = self.config["AMAZON_ADS_CLIENT_ID"]

    def _get_base_url(self, region: str) -> str:
        return AMAZON_ADS_API_BASE_ENDPOINT[region]

    def _get_headers(self, access_token: str):
        return {
            "Authorization": f"Bearer {access_token}",
            "Amazon-Advertising-API-ClientId": self.client_id,
        }

    def get_ads_profile(self, access_token: str, region: str) -> str:
        headers = self._get_headers(access_token=access_token)
        base_url = self._get_base_url(region=region)
        endpoint = "/v2/profiles"
        response = requests.get(url=base_url + endpoint, headers=headers)
        return response
