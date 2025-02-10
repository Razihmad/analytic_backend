import gzip
import json
import logging
from typing import Dict


import requests
from sp_api.base import Marketplaces


import utils.datetime as dt

logger = logging.getLogger(__name__)


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

    def create_report(self, access_token: str, marketplace: str, report_type: str, data: Dict):
        base_url = self.get_base_url(marketplace)
        marketplace_id = self.get_marketplace_id(marketplace)
        headers = self._get_headers(access_token)
        url = f"{base_url}/reports/2021-06-30/reports"
        data.update({
            "reportType": report_type,
            "marketplaceIds": [marketplace_id]
        })
        response = requests.post(url, headers=headers, json=data)
        return response.json()

    def get_report_by_id(self, access_token: str, report_id: str, marketplace: str):
        base_url = self.get_base_url(marketplace)
        headers = self._get_headers(access_token)
        url = f"{base_url}/reports/2021-06-30/reports/{report_id}"
        response = requests.get(url, headers=headers)
        return response.json()

    def get_report_document_by_id(self, access_token: str, document_id: str, marketplace: str):
        base_url = self.get_base_url(marketplace)
        headers = self._get_headers(access_token)
        url = f"{base_url}/reports/2021-06-30/documents/{document_id}"
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            
        return response.json()

    def get_data_by_url(self, url: str):
        response = requests.get(url)
        decompressed_data = gzip.decompress(response.content)
        json_data = decompressed_data.decode('utf-8')
        parsed_data = json.load(json_data)
        return parsed_data


amazon_sp_api = AmazonSpAPI()
