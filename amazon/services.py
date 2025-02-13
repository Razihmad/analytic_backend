from datetime import timedelta
from typing import Dict, List

from django.core.cache import cache
from sp_api.base import ReportStatus

import utils.datetime as dt
from amazon.models import SellerCentralSale
from amazon.selectors import bulk_create_seller_central_sales, get_seller_by_user_id
from amazon.tasks import fetch_seller_central_report_data_by_date
from utils.utils import get_cache_key_and_timeout


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


def start_fetching_seller_central_data(*, user_id: int):
    seller = get_seller_by_user_id(user_id=user_id)
    marketplace = seller.marketplace
    current_datetime = (dt.now(with_tz=True) - timedelta(days=2))
    key, _ = get_cache_key_and_timeout("REPORT_CANCELLED", seller_id=seller.id)
    status = cache.get(key, ReportStatus.IN_PROGRESS.value)
    count = 0
    while status != ReportStatus.CANCELLED.value:
        countdown = 0
        if count % 10 == 0:
            countdown = 1
        start_datetime = (current_datetime - timedelta(days=1))
        fetch_seller_central_report_data_by_date.apply_async(
            args=[user_id, seller.id, marketplace, start_datetime.strftime("%Y-%m-%dT%H:%M:%S"), current_datetime.strftime("%Y-%m-%dT%H:%M:%S")],
            countdown=countdown,
        )
        current_datetime = start_datetime
        count += 1
        if count == 2:
            break
