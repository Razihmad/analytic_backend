import logging
from datetime import timedelta
from typing import Dict, List

from django.core.cache import cache
from sp_api.base import ReportStatus

from base.exception import ServiceException
import utils.datetime as dt
from amazon.models import SellerCentralSale
from amazon.selectors import bulk_create_seller_central_sales, get_seller_by_user_id
from amazon.tasks import fetch_seller_central_report_data_by_date
from utils.utils import get_cache_key_and_timeout


logger = logging.getLogger(__name__)


def prepare_and_bulk_create_sales_data(*, data: List[Dict]):
    sales_objects = [
        SellerCentralSale(
            seller_id=sale["seller_id"],
            child_asin=sale["child_asin"],
            parent_asin=sale["parent_asin"],
            sales_date=sale["sales_date"],
            units_ordered=sale["units_ordered"],
            ordered_product_sales=sale["ordered_product_sales"],
            items_ordered=sale["items_ordered"],
        )
        for sale in data
    ]
    bulk_create_seller_central_sales(data=sales_objects)


def start_fetching_seller_central_data(*, user_id: int, amazon_seller_id: str):
    if not amazon_seller_id:
        raise ServiceException("amazon seller id is missing")

    seller = get_seller_by_user_id(user_id=user_id, amazon_seller_id=amazon_seller_id)
    if not seller:
        raise ServiceException("seller does not exists")

    marketplace = seller.marketplace
    logger.info(f"start time {dt.now(with_tz=True)=}")
    fetch_seller_central_report_data_by_date(
        user_id, seller.id, marketplace, amazon_seller_id
    )
