import gzip
import json
from typing import Dict, List, Optional, Tuple

# third party imports
import requests
from django.conf import settings

from utils.constants import AMAZON_ADS_API_BASE_ENDPOINT


class AmazonAds:
    def __init__(self):
        self.config = settings.AMAZON_ADS_CONFIG
        self.client_id = self.config["AMAZON_ADS_CLIENT_ID"]

    def _get_base_url(self, region: str) -> str:
        return AMAZON_ADS_API_BASE_ENDPOINT[region]

    def _get_headers(self, access_token: str, profile_id: Optional[str] = None) -> Dict:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Amazon-Advertising-API-ClientId": self.client_id,
        }
        if profile_id:
            headers["Amazon-Advertising-API-Scope"] = profile_id
        return headers

    def get_ads_profile(self, access_token: str, region: str) -> List[Dict]:
        headers = self._get_headers(access_token=access_token)
        base_url = self._get_base_url(region=region)
        endpoint = "/v2/profiles"
        response = requests.get(url=base_url + endpoint, headers=headers)
        return response.json()

    def prepare_payload_for_report(
        self,
        report_type: str,
        name: str,
        start_date: str,
        end_date: str,
        group_by: List[str],
        columns: List[str],
        ad_product: str,
        time_unit: str,
        filters: Optional[Dict] = None
    ) -> Dict:
        data = {
            "name": name,
            "startDate": start_date,
            "endDate": end_date,
            "configuration": {
                "adProduct": ad_product,
                "groupBy": group_by,
                "columns": columns,
                "reportTypeId": report_type,
                "timeUnit": time_unit,
                "format": "GZIP_JSON"
            },
        }
        if filters:
            data["configuration"]["filters"] = [filters]
        return data

    def create_report(self, access_token: str, region: str, profile_id: str, data: Dict) -> Dict:
        headers = self._get_headers(access_token=access_token, profile_id=profile_id)
        base_url = self._get_base_url(region=region)
        endpoint = "/reporting/reports"
        response = requests.post(url=base_url + endpoint, headers=headers, json=data)
        return response.json()

    def get_report_status_by_report_id(
        self, access_token: str, region: str, report_id: str, profile_id: str
    ) -> Dict:
        headers = self._get_headers(access_token=access_token, profile_id=profile_id)
        base_url = self._get_base_url(region=region)
        endpoint = f"/reporting/reports/{report_id}"
        response = requests.get(url=base_url + endpoint, headers=headers)
        return response.json()

    def get_data_by_url(self, url: str):
        response = requests.get(url)
        decompressed_data = gzip.decompress(response.content)
        json_data = decompressed_data.decode('utf-8')
        parsed_data = json.loads(json_data)
        return parsed_data
    
    def create_campaign(self, access_token: str, region: str, profile_id: str, data: Dict, endpoint: str) -> Dict:
        headers = self._get_headers(access_token=access_token, profile_id=profile_id)
        base_url = self._get_base_url(region=region)
        response = requests.post(url=base_url + endpoint, headers=headers, json=data)
        return response.json()

    def get_portfolio(self, access_token: str, region: str, profile_id: str) -> Dict:
        headers = self._get_headers(access_token=access_token, profile_id=profile_id)
        base_url = self._get_base_url(region=region)
        endpoint = "/v2/portfolios"
        response = requests.get(url=base_url + endpoint, headers=headers)
        return response.json()
    
    def create_portfolio(self, access_token: str, region: str, profile_id: str, data: Dict) -> Dict:
        headers = self._get_headers(access_token=access_token, profile_id=profile_id)
        base_url = self._get_base_url(region=region)
        endpoint = "/v2/portfolios"
        response = requests.post(url=base_url + endpoint, headers=headers, json=data)
        return response.json()
    
    def sp_negative_keywords(
        self,
        access_token: str,
        region: str,
        profile_id: str,
        endpoint: str,
        data: Optional[Dict] = None,
    ) -> Tuple[int, Dict]:
        headers = self._get_headers(access_token=access_token, profile_id=profile_id)
        base_url = self._get_base_url(region=region)
        headers["Content-Type"] = "application/vnd.spNegativeKeyword.v3+json"
        headers["Accept"] = "application/vnd.spnegativeKeyword.v3+json"
        url = base_url + endpoint
        if data:
            response = requests.post(url=url, headers=headers, json=data)
        else:
            response = requests.get(url=url, headers=headers)
        return response.status_code, response.json()

    def sp_keywords(
        self,
        access_token: str,
        region: str,
        profile_id: str,
        endpoint: str,
        data: Optional[Dict] = None,
    ) -> Tuple[int, Dict]:
        headers = self._get_headers(access_token=access_token, profile_id=profile_id)
        base_url = self._get_base_url(region=region)
        headers["Content-Type"] = "application/vnd.spKeyword.v3+json"
        headers["Accept"] = "application/vnd.spKeyword.v3+json"
        url = base_url + endpoint
        response = requests.post(url=url, headers=headers, json=data)
        return response.status_code, response.json()

    def update_keyword(
        self,
        access_token: str,
        region: str,
        profile_id: str,
        endpoint: str,
        data: Dict,
        content_type: str,
        accept: Optional[str] = None,
    ) -> Tuple[int, Dict]:
        headers = self._get_headers(access_token=access_token, profile_id=profile_id)
        base_url = self._get_base_url(region=region)
        headers["Content-Type"] = content_type
        if accept:
            headers["Accept"] = accept
        url = base_url + endpoint
        response = requests.put(url=url, headers=headers, json=data)
        return response.status_code, response.json()

    def add_negative_product_targeting(
        self,
        access_token: str,
        region: str,
        profile_id: str,
        endpoint: str,
        data: Dict,
        content_type: str,
        accept: Optional[str] = None
    ) -> Tuple[int, Dict]:
        headers = self._get_headers(access_token=access_token, profile_id=profile_id)
        base_url = self._get_base_url(region=region)
        headers["Content-Type"] = content_type
        if accept:
            headers["Accept"] = accept
        url = base_url + endpoint
        response = requests.post(url=url, headers=headers, json=data)
        return response.status_code, response.json()
    
    def update_targeting_by_target_id(
        self,
        access_token: str,
        region: str,
        profile_id: str,
        endpoint: str,
        data: Dict,
        content_type: str,
    ) -> Tuple[int, Dict]:
        headers = self._get_headers(access_token=access_token, profile_id=profile_id)
        base_url = self._get_base_url(region=region)
        headers["Content-Type"] = content_type
        headers["Accept"] = content_type
        url = base_url + endpoint
        response = requests.put(url=url, headers=headers, json=data)
        return response.status_code, response.json()

    # def sb_negative_targeting(
    #     self,
    #     access_token: str,
    #     region: str,
    #     profile_id: str,
    #     endpoint: str,
    #     data: Dict
    # ) -> Tuple[int, Dict]:
    #     headers = self._get_headers(access_token=access_token, profile_id=profile_id)
    #     base_url = self._get_base_url(region=region)
    #     headers["Content-Type"] = "application/json"
    #     # headers["Accept"] = "application/vnd.sbNegativeTargetingClause.v3+json"
    #     url = base_url + endpoint
    #     response = requests.post(url=url, headers=headers, json=data)
    #     return response.status_code, response.json()

amazon_ads_api = AmazonAds()
# report_id="375146d7-6e84-40ef-9626-0cb9eb60ace8"
