from utils.amazon_sp_api import sp_api


def get_amazon_login_uri(*, marketplace: str):
    return sp_api.generate_login_url(marketplace=marketplace)


def get_refresh_token(*, code: str):
    return sp_api.generate_refresh_token(code=code)
