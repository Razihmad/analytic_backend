import logging
import functools
from typing import List

from base.exception import ServiceException
from base.response import status_400, status_500
from utils.utils import get_cache_key_and_timeout

from django.core.cache import cache

logger = logging.getLogger(__name__)


def handle_exception(func: callable) -> callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ServiceException as se:
            return status_400(message=str(se))
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e=}", exc_info=True)
            return status_500(message="Something went wrong")
    return wrapper


def cache_function(*, cache_config_key: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache_key, cache_timeout = get_cache_key_and_timeout(cache_config_key, **kwargs)
            data = cache.get(cache_key)
            if data:
                return data
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout=cache_timeout)
            return result
        return wrapper
    return decorator
