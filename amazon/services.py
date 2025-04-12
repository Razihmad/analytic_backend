from collections import defaultdict
import logging
import datetime
from typing import Dict, List, Optional, Tuple


from amazon.serializers import (
    process_total_and_sales_data,
    serialize_amazon_profile_account,
    serialize_regions_details,
    serialize_seller_central_sales,
    serialize_seller_central_traffic
)
from amazon.tasks import fetch_seller_central_report_data_by_date, fetch_seller_central_return_report_data_by_date
from amazon_ads.services import get_ads_sales, verify_and_get_ads_profile
from base.exception import ServiceException
import utils.datetime as dt
from amazon.models import Seller, SellerCentralSale, SellerCentralTraffic, SellerCentralReturn
from amazon.selectors import (
    bulk_create_return_data,
    bulk_create_seller_central_sales,
    get_all_asins_of_seller,
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
            sales=sale["sales"],
            orders=sale["orders"],
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
            sessions_date=traffic["sessions_date"],
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
        args=[user_id, seller.pk, marketplace, amazon_seller_id], queue="process_report"
    )
    fetch_seller_central_return_report_data_by_date.apply_async(
        args=[user_id, seller.pk, marketplace, amazon_seller_id], queue="process_report"
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


def get_total_sales(*, seller: Seller, start_date: datetime.date, end_date: datetime.date, asins: Optional[List[str]] = None) -> List[Dict]:
    logger.info(f"{seller.user_id=}, {seller.id=} {seller.amazon_seller_id=}, {start_date=}, {end_date=}, {asins=}")
    total_sales = get_seller_central_sales_data(seller=seller, start_date=start_date, end_date=end_date, asins=asins)
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


def get_sales_report_data(
    *,
    user_id: int,
    amazon_seller_id: str,
    start_date_str: str,
    end_date_str: str,
    asins: Optional[str] = None,
    prev_start_date: str,
    prev_end_date: str,
) -> Dict:
    logger.info(f"{user_id=}, {amazon_seller_id=}, {start_date_str=}, {end_date_str=}")
    start_date = dt.convert_str_to_date(date_str=start_date_str)
    end_date = dt.convert_str_to_date(date_str=end_date_str)
    prev_start_date = dt.convert_str_to_date(date_str=prev_start_date)
    prev_end_date = dt.convert_str_to_date(date_str=prev_end_date)
    seller = verify_and_get_seller(user_id=user_id, amazon_seller_id=amazon_seller_id)
    current_period_total_sales = get_total_sales(seller=seller, start_date=start_date, end_date=end_date, asins=asins)
    prev_period_total_sales = get_total_sales(seller=seller, start_date=prev_start_date, end_date=prev_end_date, asins=asins)
    ads_profile = verify_and_get_ads_profile(user_id=user_id, amazon_seller_id=amazon_seller_id)
    current_total_traffic = get_total_traffic(seller=seller, start_date=start_date, end_date=end_date)
    prev_total_traffiic = get_total_traffic(seller=seller, start_date=prev_start_date, end_date=prev_end_date)

    current_period_ads_sales = get_ads_sales(
        ads_profile=ads_profile, start_date=start_date, end_date=end_date, asins=asins
    )
    prev_period_ads_sales = get_ads_sales(
        ads_profile=ads_profile, start_date=prev_start_date, end_date=prev_end_date, asins=asins
    )
    current_period_report = process_total_and_sales_data(
        total_sales=current_period_total_sales, ads_sale=current_period_ads_sales, traffic_data=current_total_traffic
    )
    previos_period_report = process_total_and_sales_data(
        total_sales=prev_period_total_sales, ads_sale=prev_period_ads_sales, traffic_data=prev_total_traffiic,
    )
    report = get_values_delta_and_percentage_change(
        previous_report=previos_period_report, current_report=current_period_report
    )
    # performer_asins = get_top_performer_asins(sales_data=current_period_total_sales)
    return report


def get_available_regions() -> List[Dict]:
    regions = get_regions()
    serialized_regions = serialize_regions_details(regions=regions)
    return serialized_regions


def get_amazon_accounts_profile(*, user_id: int) -> List[Dict]:
    accounts = get_amazon_accounts_profile_by_user_id(user_id=user_id)
    serialized_accounts = [serialize_amazon_profile_account(profile=profile) for profile in accounts]
    return serialized_accounts


def get_seller_asins(*, user_id: int, amazon_seller_id: str):
    seller = get_seller_by_user_id(user_id=user_id, amazon_seller_id=amazon_seller_id)
    if not seller:
        raise ServiceException("seller does not exists")
    asins = get_all_asins_of_seller(seller_id=seller.id)
    return asins


def get_top_performer_asins(*, sales_data: List[Dict]):
    total_sales = 0
    asin_wise_sales = defaultdict(int)
    for data in sales_data:
        total_sales += data["sales"]
        asin_wise_sales[data["child_asin"]] += data["sales"]
    cur_sales = 0
    top_asins = []
    for asin in sorted(asin_wise_sales.keys(), reverse=True):
        sales = asin_wise_sales[asin]
        cur_sales += sales
        top_asins.append(asin)
        if cur_sales >= total_sales * 0.8:
            break
    performer_asin_with_sales = {
        asin: get_percentage(cur_value=asin_wise_sales[asin], total_value=total_sales) for asin in top_asins
    }

    return performer_asin_with_sales


def get_percentage(*, cur_value: int, total_value: int):
    return round((cur_value / total_value) * 100, 2)


def get_asin_categorization_by_sales(*, user_id: int, amazon_seller_id: int, start_date: str, end_date: str) -> Tuple[List, List, List]:
    logger.info(f"{start_date=}, {end_date=}, {user_id=}, {amazon_seller_id=}")
    start_date = dt.convert_str_to_date(date_str=start_date)
    end_date = dt.convert_str_to_date(date_str=end_date)
    seller = get_seller_by_user_id(user_id=user_id, amazon_seller_id=amazon_seller_id)
    logger.info(f"{start_date=}, {end_date=}, {user_id=}, {seller=}")
    total_sales_data = get_total_sales(seller=seller, start_date=start_date, end_date=end_date)
    total_traffic_data = get_total_traffic(seller=seller, start_date=start_date, end_date=end_date)
    ads_sales_data = get_ads_sales(
        ads_profile=seller, start_date=start_date, end_date=end_date
    )
    total_sales = 0
    for data in total_sales_data:
        total_sales += data["sales"]
    asin_greater_than_5_percent, tier_1_asins_count = [], 0
    asin_greater_than_1_percent, tier_2_asins_count = [], 0
    asin_less_than_1_percent, tier_3_asins_count = [], 0
    asin_wise_sales = defaultdict(dict)
    for data in total_sales_data:
        cur_data = asin_wise_sales[data["child_asin"]]
        ads_sales, ads_spend = get_ad_sales_by_asin(total_ads_sales=ads_sales_data, asin=data["child_asin"])
        cur_data["ads_sales"] = cur_data.get("ads_sales", 0) + ads_sales
        cur_data["ads_spend"] = cur_data.get("ads_spend", 0) + ads_spend
        total_sessions, sku = get_sessions_and_sku_of_asin(traffic_data=total_traffic_data, asin=data["child_asin"])
        cur_data["total_sessions"] = total_sessions + cur_data.get("total_sessions", 0)
        cur_data["sku"] = sku
        cur_data["sales"] = cur_data.get("sales", 0) + data["sales"]
        cur_data["orders"] = cur_data.get("orders", 0) + data["orders"]
        cur_data["units_ordered"] = data["units_ordered"] + cur_data.get("units_ordered", 0)
        cur_data["asin"] = data["child_asin"]
        asin_wise_sales[data["child_asin"]] = cur_data

    for _, data in asin_wise_sales.items():
        data["cvr"] = round(float(data["orders"]) / float(data["total_sessions"]), 2) if data.get("total_sessions") else 0
        data["tacos"] = round(float(data["ads_spend"]) / float(data["sales"])) if data.get("sales") else 0
        data["acos"] = round(float(data["ads_spend"]) / float(data["ads_sales"])) if data.get("ads_sales") else 0
        if data["sales"] > total_sales * 0.05:
            asin_greater_than_5_percent.append(data)
            tier_1_asins_count += 1
        elif data["sales"] > total_sales * 0.01:
            asin_greater_than_1_percent.append(data)
            tier_2_asins_count += 1
        else:
            asin_less_than_1_percent.append(data)
            tier_3_asins_count += 1

    total_asins = len(total_sales_data)
    logger.info(f"{start_date=}, {end_date=}, {user_id=}, {seller=}, {total_asins=}")
    if not total_asins:
        return {}, {}, {}
    tier_1_data = {"asin_percentage": round(100 * tier_1_asins_count / total_asins, 2), "data": asin_greater_than_5_percent}
    tier_2_data = {"asin_percentage": round(100 * tier_2_asins_count / total_asins, 2), "data": asin_greater_than_1_percent}
    tier_3_data = {"asin_percentage": round(100 * tier_3_asins_count / total_asins, 2), "data": asin_less_than_1_percent}
    return tier_1_data, tier_2_data, tier_3_data


def get_sessions_and_sku_of_asin(*, traffic_data: List[Dict], asin: str) -> Tuple[int, str]:
    for data in traffic_data:
        if data.get("child_asin", "") == asin:
            return data["total_sessions"], data["sku"]
    return 0, ""


def get_ad_sales_by_asin(*, total_ads_sales: List[Dict], asin: str) -> int:
    for data in total_ads_sales:
        if data.get("asin", "") == asin:
            return data["sales"], data["spend"]
    return 0, 0
