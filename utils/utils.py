import json
import xmltodict

from sp_api.base import Marketplaces

from project.cache_config import CACHE_NAMES


def get_cache_key_and_timeout(dict_identifier, **kwargs):
    cache_dict = CACHE_NAMES[dict_identifier]
    cache_key = cache_dict["key"].format(**kwargs)
    if callable(cache_dict["timeout"]):
        cache_timeout = cache_dict["timeout"]()
    else:
        cache_timeout = cache_dict["timeout"]
    return cache_key, cache_timeout


def convert_xml_to_json(*, xml_data):
    data = xmltodict.parse(xml_data)
    return json.dumps(data)


def get_region_by_country_code(*, country_code: str) -> str:
    marketplace = getattr(Marketplaces, country_code.upper())
    return marketplace.region
