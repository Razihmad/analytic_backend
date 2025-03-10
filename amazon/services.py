import logging
from typing import Dict, List


from base.exception import ServiceException
import utils.datetime as dt
from amazon.models import SellerCentralSale, SellerCentralTraffic, SellerCentralReturn
from amazon.selectors import bulk_create_return_data, bulk_create_seller_central_sales, get_seller_by_user_id, bulk_create_seller_central_traffic
from amazon.tasks import fetch_seller_central_report_data_by_date, fetch_seller_central_return_report_data_by_date


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


def prepare_and_bulk_create_traffic_data(*, data: List[Dict]):
    traffic_objects = [
        SellerCentralTraffic(
            seller_id=traffic["seller_id"],
            child_asin=traffic["child_asin"],
            sku=traffic["sku"],
            session_date=traffic["session_date"],
            browser_sessions=traffic["browser_sessions"],
            mobile_app_sessions=traffic["mobile_app_sessions"],
            browser_page_views=traffic["browser_page_views"],
            mobile_app_page_views=traffic["mobile_app_page_views"],
            unit_sessions_percentage=traffic["unit_sessions_percentage"]
        )
        for traffic in data
    ]
    bulk_create_seller_central_traffic(data=traffic_objects)


def start_fetching_seller_central_data(*, user_id: int, amazon_seller_id: str):
    if not amazon_seller_id:
        raise ServiceException("amazon seller id is missing")

    seller = get_seller_by_user_id(user_id=user_id, amazon_seller_id=amazon_seller_id)
    if not seller:
        raise ServiceException("seller does not exists")

    marketplace = seller.marketplace
    logger.info(f"start time {dt.now(with_tz=True)=}")
    fetch_seller_central_report_data_by_date.apply_async(
        args=[user_id, seller.id, marketplace, amazon_seller_id]
    )
    fetch_seller_central_return_report_data_by_date.apply_async(
        args=[user_id, seller.id, marketplace, amazon_seller_id]
    )


def prepare_bulk_create_return_data(*, data: List[Dict]):
    return_objects = [
        SellerCentralReturn(
            seller_id=return_data["seller_id"],
            asin=return_data["asin"],
            return_delivery_date=return_data["return_delivery_date"],
            return_type=return_data["return_type"],
            return_request_date=return_data["return_request_date"],
            refund_amount=return_data["refund_amount"],
            return_quantity=return_data["return_quantity"],
        )
        for return_data in data
    ]
    bulk_create_return_data(data=return_objects)


def get_sales_data(*, user_id: int, amazon_seller_id: str, start_date: str, end_date: str):
    if not amazon_seller_id:
        raise ServiceException("amazon seller id is missing")

    seller = get_seller_by_user_id(user_id=user_id, amazon_seller_id=amazon_seller_id)
    if not seller:
        raise ServiceException("seller does not exists")

    marketplace = seller.marketplace
    logger.info(f"start time {dt.now(with_tz=True)=}")
