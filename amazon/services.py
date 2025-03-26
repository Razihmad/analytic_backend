import logging
import datetime
from typing import Dict, List


from amazon.serializers import process_total_and_sales_data, serialize_amazon_profile_account, serialize_regions_details, serialize_seller_central_sales, serialize_seller_central_traffic
from amazon.tasks import fetch_seller_central_report_data_by_date, fetch_seller_central_return_report_data_by_date
from amazon_ads.services import get_ads_sales, verify_and_get_ads_profile
from base.exception import ServiceException
import utils.datetime as dt
from amazon.models import Seller, SellerCentralSale, SellerCentralTraffic, SellerCentralReturn
from amazon.selectors import (
    bulk_create_return_data,
    bulk_create_seller_central_sales,
    get_amazon_accounts_profile_by_user_id,
    get_regions,
    get_seller_by_user_id,
    bulk_create_seller_central_traffic,
    get_seller_central_sales_data,
    get_seller_central_traffic_data
)
from utils.utils import get_values_delta_and_percentage_change


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
        args=[user_id, seller.pk, marketplace, amazon_seller_id]
    )
    fetch_seller_central_return_report_data_by_date.apply_async(
        args=[user_id, seller.pk, marketplace, amazon_seller_id]
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


def get_total_sales(*, seller: Seller, start_date: datetime.date, end_date: datetime.date) -> List[Dict]:
    logger.info(f"{seller.user_id=}, {seller.id=} {seller.amazon_seller_id=}, {start_date=}, {end_date=}")
    total_sales = get_seller_central_sales_data(seller=seller, start_date=start_date, end_date=end_date)
    total_sales_data = serialize_seller_central_sales(sales=total_sales)
    return total_sales_data


def get_total_traffic(*, seller: Seller, start_date: datetime.date, end_date: datetime.date) -> List[Dict]:
    logger.info(f"{seller.pk=}, {start_date=}, {end_date=}")
    total_traffic = get_seller_central_traffic_data(seller=seller, start_date=start_date, end_date=end_date)
    total_traffic_data = serialize_seller_central_traffic(traffics=total_traffic)
    return total_traffic_data


def verify_and_get_seller(*, user_id: int, amazon_seller_id: str) -> Seller:
    if not amazon_seller_id:
        raise ServiceException("amazon seller id is missing")

    seller = get_seller_by_user_id(user_id=user_id, amazon_seller_id=amazon_seller_id)
    if not seller:
        raise ServiceException("seller does not exists")

    return seller


def get_sales_report_data(*, user_id: int, amazon_seller_id: str, start_date_str: str, end_date_str: str) -> Dict:
    logger.info(f"{user_id=}, {amazon_seller_id=}, {start_date_str=}, {end_date_str=}")
    start_date = dt.convert_str_to_date(date_str=start_date_str)
    end_date = dt.convert_str_to_date(date_str=end_date_str)
    prev_start_date, prev_end_date = dt.get_previous_period_of_dates(start_date=start_date, end_date=end_date)
    seller = verify_and_get_seller(user_id=user_id, amazon_seller_id=amazon_seller_id)
    current_period_total_sales = get_total_sales(seller=seller, start_date=start_date, end_date=end_date)
    prev_period_total_sales = get_total_sales(seller=seller, start_date=prev_start_date, end_date=prev_end_date)
    ads_profile = verify_and_get_ads_profile(user_id=user_id, amazon_seller_id=amazon_seller_id)

    current_period_ads_sales = get_ads_sales(
        ads_profile=ads_profile, start_date=start_date, end_date=end_date
    )
    prev_period_ads_sales = get_ads_sales(
        ads_profile=ads_profile, start_date=prev_start_date, end_date=prev_end_date
    )
    current_period_report = process_total_and_sales_data(
        total_sales=current_period_total_sales, ads_sale=current_period_ads_sales
    )
    previos_period_report = process_total_and_sales_data(
        total_sales=prev_period_total_sales, ads_sale=prev_period_ads_sales
    )
    report = get_values_delta_and_percentage_change(
        previous_report=previos_period_report, current_report=current_period_report
    )
    return report


def get_available_regions() -> List[Dict]:
    regions = get_regions()
    serialized_regions = serialize_regions_details(regions=regions)
    return serialized_regions


def get_amazon_accounts_profile(*, user_id: int) -> List[Dict]:
    accounts = get_amazon_accounts_profile_by_user_id(user_id=user_id)
    serialized_accounts = [serialize_amazon_profile_account(profile=profile) for profile in accounts]
    return serialized_accounts
