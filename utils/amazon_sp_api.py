from django.conf import settings
from sp_api.base import Marketplaces


class AmazonSpApi:
    def __init__(self):
        self.config = settings.AMAZON_CONFIG
        self.client_id = self.config["AMAZON_CLIENT_ID"]
        self.client_secret = self.config["AMAZON_CLIENT_SECRET"]
        self.app_id = self.config["AMAZON_APP_ID"]

    def generate_login_url(self, marketplace: str):
        marketplace_data = getattr(Marketplaces, marketplace.upper())
        base_url = marketplace_data.endpoint
        marketplace_id = marketplace_data.marketplace_id
        # return f"{base_url}/apps/authorize/consent?application_id={self.client_id}&scope=advertising::campaigns&response_type=code&state={marketplace_id}&redirect_uri=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        return f"{base_url}/apps/authorize/consent?application_id={self.app_id}&state={marketplace_id}&version=beta"

    def url_for_generating_token(self, code: str, marketplace: str):
        marketplace_data = getattr(Marketplaces, marketplace.upper())
        base_url = marketplace_data.endpoint
        # return f"{base_url}/auth/token" + "?" + f"grant_type=authorization_code&code={code}&client_id={self.client_id}&client_secret={self.client_secret}" + "&scope=advertising::campaigns"
        return f"{base_url}//auth/o2/token?grant_type=authorization_code&code={code}&client_id={self.client_id}&client_secret={self.client_secret}"

    def generate_refresh_token(self, code: str, marketplace: str):
        url = self.url_for_generating_token(code=code, marketplace=marketplace)
        import requests
        response = requests.post(url)
        print(response.status_code)
        print(response.text)
        # print(response.json())
        return response.json()


sp_api = AmazonSpApi()
