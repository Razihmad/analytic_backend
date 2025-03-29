import json
import xmltodict

from sp_api.base import Marketplaces

from project.cache_config import CACHE_NAMES
from typing import Dict


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


def get_values_delta_and_percentage_change(*, previous_report: Dict, current_report: Dict) -> Dict:
    changes = {}
    for key in previous_report:
        prev_value = previous_report[key]
        curr_value = current_report[key]
        absolute_change = curr_value - prev_value
        percentage_change = 0
        if prev_value != 0:
            percentage_change = (absolute_change / prev_value) * 100
        changes[key] = {
            'previous': prev_value,
            'current': curr_value,
            'absolute_change': absolute_change,
            'percentage_change': round(percentage_change, 2),
            "color": "green" if percentage_change > 0 else "red",
            "arrow": "up" if percentage_change > 0 else "down"
        }
    return changes
