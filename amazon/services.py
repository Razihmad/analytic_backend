from datetime import timedelta
from typing import Dict, List

import utils.datetime as dt
from amazon.models import SellerCentralSale
from amazon.selectors import bulk_create_seller_central_sales, get_seller_by_user_id
from amazon.tasks import fetch_seller_central_report_data_by_date



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
    end_datetime = (dt.now(with_tz=True) - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
    start_datetime = (dt.now(with_tz=True) - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%S.%f%z")
    fetch_seller_central_report_data_by_date.delay(
        user_id=user_id, seller_id=seller.id, marketplace=marketplace, start_datetime=start_datetime, end_datetime=end_datetime
    )
