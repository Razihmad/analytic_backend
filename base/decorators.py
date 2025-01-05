import logging
import functools

from base.exception import ServiceException
from base.response import status_400, status_500

logger = logging.getLogger(__name__)


def handle_exception(func: callable) -> callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ServiceException as se:
            return status_400(message=str(se))
        except Exception as e:
            logger.error(f"Unexpected error occurred: {e}")
            return status_500(message="Something went wrong")
    return wrapper
