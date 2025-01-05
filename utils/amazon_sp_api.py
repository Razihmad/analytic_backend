from typing import Dict
from sp_api.base import Marketplaces
# from sp_api.base import ReportType


import utils.datetime as dt


class AmazonSpAPI:
    def get_base_url(self, marketplace: str):
        marketplace = getattr(Marketplaces, marketplace.upper())
        return marketplace.endpoint

    def get_marketplace_id(self, marketplace: str):
        marketplace = getattr(Marketplaces, marketplace.upper())
        return marketplace.marketplace_id

    def get_region(self, marketplace: str):
        marketplace = getattr(Marketplaces, marketplace.upper())
        return marketplace.region

    def _get_headers(self, access_token: str) -> Dict:
        return {
            "x-amz-access-token": access_token,
            "x-amz-date": dt.now(with_tz=True).strftime('%Y%m%dT%H%M%SZ'),
        }


amazon_sp_api = AmazonSpAPI()
