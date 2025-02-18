import json
import xmltodict

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
