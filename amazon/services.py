from collections import defaultdict
import logging
import datetime
from typing import Dict, List, Optional, Tuple

from click import group


from amazon.serializers import (
    group_total_sales_data_by_date,
    process_total_and_sales_data,
    serialize_ads_sales_with_asin_mapper,
    serialize_amazon_profile_account,
    serialize_regions_details,
    serialize_seller_central_sales,
    serialize_seller_central_sales_with_asin_mapper,
    serialize_seller_central_traffic,
    serialize_seller_central_traffic_with_asin_mapper
)
from amazon.tasks import fetch_seller_central_report_data_by_date, fetch_seller_central_return_report_data_by_date
from amazon_ads.constants import GraphDataType
from amazon_ads.selectors import get_ads_sales_data
from amazon_ads.services import get_ads_data_for_graph, get_ads_sales, get_campaign_sales_data, verify_and_get_ads_profile
from authentication.services import get_access_token
from base.exception import ServiceException
import utils.datetime as dt
from amazon.models import SearchQueryMarketBasket, Seller, SellerCentralSale, SellerCentralTraffic, SellerCentralReturn
from amazon.selectors import (
    bulk_create_return_data,
    bulk_create_search_query_market_basket,
    bulk_create_seller_central_sales,
    get_all_asins_of_seller,
    get_amazon_accounts_profile_by_user_id,
    get_asin_mapper_by_asins,
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
            sku=sale["sku"],
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

def prepare_and_bulk_create_search_query_market_basket_data(*, data: List[Dict]):
    search_query_market_basket_objects = [
        SearchQueryMarketBasket(
            seller_id=data["seller_id"],
            asin=data["asin"],
            purchased_with_asin=data["purchased_with_asin"],
            purchased_with_rank=data["purchased_with_rank"],
            combination_pct=data["combination_pct"],
            report_period=data["report_period"],
            start_date=data["start_date"],
            end_date=data["end_date"],
        )
    ]
    bulk_create_search_query_market_basket(data=search_query_market_basket_objects)


def get_total_sales(
    *, seller: Seller,
    start_date: datetime.date,
    end_date: datetime.date,
    asins: Optional[List[str]] = None,
    fields: Optional[List[str]] = None,
) -> List[Dict]:
    logger.info(f"{seller.user_id=}, {seller.id=} {seller.amazon_seller_id=}, {start_date=}, {end_date=}, {asins=}")
    total_sales = get_seller_central_sales_data(seller=seller, start_date=start_date, end_date=end_date, asins=asins, fields=fields)
    total_sales_data = serialize_seller_central_sales(sales=total_sales)
    return total_sales_data


def get_total_traffic(*, seller: Seller, start_date: datetime.date, end_date: datetime.date, asins: Optional[List[str]] = None) -> List[Dict]:
    logger.info(f"{seller.pk=}, {start_date=}, {end_date=}, {asins=}")
    total_traffic = get_seller_central_traffic_data(seller=seller, start_date=start_date, end_date=end_date, asins=asins)
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
    prev_start_date: str,
    prev_end_date: str,
) -> Dict:
    logger.info(f"{user_id=}, {amazon_seller_id=}, {start_date_str=}, {end_date_str=}")
    start_date = dt.convert_str_to_date(date_str=start_date_str)
    end_date = dt.convert_str_to_date(date_str=end_date_str)
    prev_start_date = dt.convert_str_to_date(date_str=prev_start_date)
    prev_end_date = dt.convert_str_to_date(date_str=prev_end_date)
    seller = verify_and_get_seller(user_id=user_id, amazon_seller_id=amazon_seller_id)
    current_period_total_sales = get_total_sales(seller=seller, start_date=start_date, end_date=end_date)
    prev_period_total_sales = get_total_sales(seller=seller, start_date=prev_start_date, end_date=prev_end_date)
    current_total_traffic = get_total_traffic(seller=seller, start_date=start_date, end_date=end_date)
    prev_total_traffiic = get_total_traffic(seller=seller, start_date=prev_start_date, end_date=prev_end_date)

    current_period_ads_sales = get_campaign_sales_data(
        seller=seller, start_date=start_date, end_date=end_date
    )
    prev_period_ads_sales = get_campaign_sales_data(
        seller=seller, start_date=prev_start_date, end_date=prev_end_date
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


def get_asin_categorization_by_sales(
    *,
    user_id: int,
    amazon_seller_id: int,
    start_date: str,
    end_date: str,
    prev_start_date: str,
    prev_end_date: str,
    group_by: str,
) -> Tuple[List, List, List]:
    group_by = group_by.lower()

    logger.info(f"{start_date=}, {end_date=}, {user_id=}, {amazon_seller_id=}, {prev_start_date=}, {prev_end_date=}")
    start_date = dt.convert_str_to_date(date_str=start_date)
    end_date = dt.convert_str_to_date(date_str=end_date)
    prev_start_date = dt.convert_str_to_date(date_str=prev_start_date)
    prev_end_date = dt.convert_str_to_date(date_str=prev_end_date)
    seller = get_seller_by_user_id(user_id=user_id, amazon_seller_id=amazon_seller_id)
    logger.info(f"{start_date=}, {end_date=}, {user_id=}, {seller=}")

    total_sales_data = get_total_sales(seller=seller, start_date=start_date, end_date=end_date)

    asins = set()
    for data in total_sales_data:
        asins.add(data["child_asin"])

    asin_mapper = get_asin_mapper_by_asins(asins=asins)
    asin_mapper_dict = {(asin_mapper.asin, asin_mapper.sku): asin_mapper for asin_mapper in asin_mapper}
    total_sales_data = serialize_seller_central_sales_with_asin_mapper(total_sales_data=total_sales_data, asin_mapper_dict=asin_mapper_dict)
    prev_total_sales_data = get_total_sales(seller=seller, start_date=prev_start_date, end_date=prev_end_date)
    prev_total_sales_data = serialize_seller_central_sales_with_asin_mapper(total_sales_data=prev_total_sales_data, asin_mapper_dict=asin_mapper_dict)

    total_traffic_data = get_total_traffic(seller=seller, start_date=start_date, end_date=end_date)
    total_traffic_data = serialize_seller_central_traffic_with_asin_mapper(traffics=total_traffic_data, asin_mapper_dict=asin_mapper_dict)
    total_traffic_data = group_sessions_and_sku_by_key(traffic_data=total_traffic_data, group_by=group_by)

    prev_total_traffic_data = get_total_traffic(seller=seller, start_date=prev_start_date, end_date=prev_end_date)
    prev_total_traffic_data = serialize_seller_central_traffic_with_asin_mapper(traffics=prev_total_traffic_data, asin_mapper_dict=asin_mapper_dict)
    prev_total_traffic_data = group_sessions_and_sku_by_key(traffic_data=prev_total_traffic_data, group_by=group_by)


    ads_sales_data = get_ads_sales_data(
        profile=seller, start_date=start_date, end_date=end_date, fields=["sales", "spend", "asin", "sku", "clicks", "impressions"], asins=None
    )
    prev_ads_sales_data = get_ads_sales_data(
        profile=seller, start_date=prev_start_date, end_date=prev_end_date, fields=["sales", "spend", "asin", "sku", "clicks", "impressions"], asins=None
    )
    ads_sales_data = serialize_ads_sales_with_asin_mapper(ads_sales_data=ads_sales_data, asin_mapper_dict=asin_mapper_dict)
    prev_ads_sales_data = serialize_ads_sales_with_asin_mapper(ads_sales_data=prev_ads_sales_data, asin_mapper_dict=asin_mapper_dict)

    ads_sales_data = group_ads_data_by_field(total_ads_sales=ads_sales_data, group_by=group_by)
    logger.info(f"[{group_by=}]{ads_sales_data=}, {prev_ads_sales_data=}")
    prev_ads_sales_data = group_ads_data_by_field(total_ads_sales=prev_ads_sales_data, group_by=group_by)

    asin_wise_sales = defaultdict(dict)
    total_spend = 0
    total_sales = 0
    for data in total_sales_data:
        key = data[group_by] # group_by can be asin, product, product_type, brand
        cur_data = asin_wise_sales[key]
        ads_sales, ads_spend, ads_clicks, impressions = get_ad_sales_by_key(ads_sales_by_asin=ads_sales_data, key=key)
        cur_data["ads_sales"] = int(ads_sales)
        cur_data["ads_spend"] = int(ads_spend)
        cur_data["ads_clicks"] = int(ads_clicks)
        cur_data["impressions"] = int(impressions)
        total_spend += int(ads_spend)
        total_sales += data["sales"]

        total_sessions_and_sku = total_traffic_data.get(key, [0, ""])
        cur_data["total_sessions"] = total_sessions_and_sku[0]
        cur_data["sku"] = total_sessions_and_sku[1]
        cur_data["sales"] = cur_data.get("sales", 0) + data["sales"]
        cur_data["orders"] = cur_data.get("orders", 0) + data["orders"]
        cur_data["units_ordered"] = data["units_ordered"] + cur_data.get("units_ordered", 0)
        cur_data[group_by] = data[group_by]
        asin_wise_sales[data[group_by]] = cur_data
    prev_total_spend = 0
    prev_total_sales = 0
    for data in prev_total_sales_data:
        key = data[group_by] # group_by can be asin, product, product_type, brand
        cur_data = asin_wise_sales[data[group_by]]
        prev_ads_sales, prev_ads_spend, prev_ads_clicks, prev_impressions = get_ad_sales_by_key(ads_sales_by_asin=prev_ads_sales_data, key=key)
        cur_data["prev_ads_sales"] = int(prev_ads_sales)
        cur_data["prev_ads_spend"] = int(prev_ads_spend)
        cur_data["prev_ads_clicks"] = int(prev_ads_clicks)
        cur_data["prev_impressions"] = int(prev_impressions)
        prev_total_spend += prev_ads_spend
        prev_total_sales += data["sales"]
        prev_total_sessions_and_sku = prev_total_traffic_data.get(key, [0, ""])
        cur_data["prev_total_sessions"] = prev_total_sessions_and_sku[0]
        cur_data["prev_sku"] = prev_total_sessions_and_sku[1]
        cur_data["prev_sales"] = cur_data.get("prev_sales", 0) + data["sales"]
        cur_data["prev_orders"] = cur_data.get("prev_orders", 0) + data["orders"]
        cur_data["prev_units_ordered"] = data["units_ordered"] + cur_data.get("prev_units_ordered", 0)
        asin_wise_sales[data[group_by]] = cur_data

    logger.info(f"{asin_wise_sales=}")
    result = []
    for key, data in asin_wise_sales.items():
        sales = int(data.get("sales"))
        prev_sales = int(data.get("prev_sales", 0))
        ads_sales = int(data.get("ads_sales"))
        prev_ads_sales = int(data.get("prev_ads_sales", 0))
        prev_ads_spend = int(data.get("prev_ads_spend", 0))
        prev_orders = int(data.get("prev_orders", 0))
        prev_total_sessions = int(data.get("prev_total_sessions", 0))
        spend_percentage = round(100 * float(data["ads_spend"]) / total_spend, 1) if total_spend else 0
        prev_spend_percentage = round(100 * float(prev_ads_spend) / prev_total_spend, 1) if prev_total_spend else 0
        organic_sales = sales - ads_sales
        organic_sales_percentage = round(100 * organic_sales / sales, 1) if sales else 0
        prev_organic_sales = prev_sales - prev_ads_sales
        prev_organic_sales_percentage = round(100 * prev_organic_sales / prev_sales, 1) if prev_sales else 0
        total_sales_percentage = round(100 * sales / total_sales, 1) if total_sales else 0
        prev_total_sales_percentage = round(100 * prev_sales / prev_total_sales, 1) if prev_total_sales else 0
        ads_clicks = int(data.get("ads_clicks", 0))
        prev_ads_clicks = int(data.get("prev_ads_clicks", 0))
        ctr = round(100 * float(data["ads_clicks"]) / float(data["impressions"]), 2) if data.get("impressions") else 0
        prev_ctr = round(100 * float(data["prev_ads_clicks"]) / float(data["prev_impressions"]), 2) if data.get("prev_impressions") else 0

        data["cvr"] = round(100 * float(data["orders"]) / float(data["total_sessions"]), 1) if data.get("total_sessions") else 0
        data["prev_cvr"] = round(100 * prev_orders / prev_total_sessions, 1) if prev_total_sessions else 0
    
        data["tacos"] = round(100 * float(data["ads_spend"]) / sales, 1) if sales else 0
        data["prev_tacos"] = round(100 * prev_ads_spend / prev_sales, 1) if prev_sales else 0

        data["acos"] = round(100 * float(data["ads_spend"]) / ads_sales, 1) if ads_sales else 0
        data["prev_acos"] = round(100 * prev_ads_spend / prev_ads_sales, 1) if prev_ads_sales else 0
        data["ads_spend_percentage"] = spend_percentage
        data["prev_ads_spend_percentage"] = prev_spend_percentage
        data["organic_sales_percentage"] = organic_sales_percentage
        data["prev_organic_sales_percentage"] = prev_organic_sales_percentage
        data["total_sales_percentage"] = total_sales_percentage
        data["prev_total_sales_percentage"] = prev_total_sales_percentage
        data["cpc"] = round(100 * float(data["ads_spend"]) / float(ads_clicks), 1) if ads_clicks else 0
        data["prev_cpc"] = round(100 * prev_ads_spend / prev_ads_clicks, 1) if prev_ads_clicks else 0
        data["ctr"] = ctr
        data["prev_ctr"] = prev_ctr
        data["sales"] = int(sales)
        data["prev_sales"] = int(prev_sales)
        data["ads_sales"] = int(ads_sales)
        data["prev_ads_sales"] = int(prev_ads_sales)
        data["ads_spend"] = int(ads_spend)
        data["prev_ads_spend"] = int(prev_ads_spend)
    
        result.append(data)


    total_asins = len(total_sales_data)
    logger.info(f"{start_date=}, {end_date=}, {user_id=}, {seller=}, {total_asins=}")
    if not total_asins:
        return {}

    return result

def group_sessions_and_sku_by_key(*, traffic_data: List[Dict], group_by: str) -> Tuple[int, str]:
    result = defaultdict(list)
    for data in traffic_data:
        key = data[group_by]
        cur_result = result[key]
        if not cur_result:
            cur_result = [0, ""]
        else:
            cur_result[0] += data["total_sessions"]
            cur_result[1] = data["sku"]
        result[key] = cur_result
    return result



def get_sessions_and_sku_of_asin(*, traffic_data: List[Dict], asin: str, group_by: str) -> Tuple[int, str]:
    total_sessions = 0
    sku = ""
    for data in traffic_data:
        if data.get(group_by, "") == asin:
            total_sessions += data["total_sessions"]
            sku = data["sku"]
    return total_sessions, sku


def get_ad_sales_by_key(*, ads_sales_by_asin: List[Dict], key: str) -> Tuple[int, int, int, int]:
    data = ads_sales_by_asin.get(key, [])
    if not data:
        return 0, 0, 0, 0
    return data[0], data[1], data[2], data[3]


def group_ads_data_by_field(*, total_ads_sales: List[Dict], group_by: str) -> Dict:
    result = defaultdict(list)
    for data in total_ads_sales:
        key = data[group_by] # group_by can be asin, product, product_type, brand
        cur_result = result[key]
        if not cur_result:
            cur_result = [0, 0, 0, 0]
        cur_result[0] += data["sales"]
        cur_result[1] += data["spend"]
        cur_result[2] += data["clicks"]
        cur_result[3] += data["impressions"]
        result[key] = cur_result

    return result


def get_graph_data_for_total_sales_data(*, seller: Seller, start_date: datetime.date, end_date: datetime.date, asins: Optional[List[str]], graph_data_type: str) -> Dict:
    logger.info(f"{seller=}, {start_date=}, {end_date=}, {asins=}, {graph_data_type=}")
    field = GraphDataType[graph_data_type]
    fields = [field.value]
    if graph_data_type in [GraphDataType.IMPRESSIONS.name, GraphDataType.CLICKS.name, GraphDataType.SPEND.name, GraphDataType.TRAFFIC.name]:
        return get_ads_data_for_graph(
            seller=seller,
            start_date=start_date,
            end_date=end_date,
            asins=asins,
            graph_data_type=graph_data_type,
        )
    total_sales_data = get_seller_central_sales_data(seller=seller, start_date=start_date, end_date=end_date, asins=asins, fields=fields)
    return group_total_sales_data_by_date(total_sales_data=total_sales_data, field=field.value)


def get_graph_data_for_organic_and_ads_sales_data(
    *, seller: Seller, start_date: datetime.date, end_date: datetime.date, asins: Optional[List[str]], graph_data_type: str
):
    total_sales_data = get_graph_data_for_total_sales_data(
        seller=seller,
        start_date=start_date,
        end_date=end_date,
        asins=asins,
        graph_data_type=graph_data_type,
    )
    ads_sales_data = get_ads_data_for_graph(
        seller=seller,
        start_date=start_date,
        end_date=end_date,
        asins=asins,
        graph_data_type=graph_data_type,
    )
    organic_data = defaultdict(int)
    for date, value in total_sales_data.items():
        organic_data[date] += (value - ads_sales_data.get(date, 0))
    return organic_data, ads_sales_data


def get_data_for_graph(
    *, user_id: int, amazon_seller_id: str, start_date: str, end_date: str, asins: Optional[List[str]], graph_data_type: str, prev_start_date: str, prev_end_date: str
) -> Tuple[Dict, Dict]:
    logger.info(f"{user_id=}, {amazon_seller_id=}, {start_date=}, {end_date=}, {asins=}, {graph_data_type=}")
    start_date = dt.convert_str_to_date(date_str=start_date)
    end_date = dt.convert_str_to_date(date_str=end_date)
    prev_start_date = dt.convert_str_to_date(date_str=prev_start_date)
    prev_end_date = dt.convert_str_to_date(date_str=prev_end_date)
    seller = get_seller_by_user_id(user_id=user_id, amazon_seller_id=amazon_seller_id)
    if not seller:
        raise ServiceException(f"seller does not exist {amazon_seller_id=}, {user_id=}")
    return get_graph_data_for_total_sales_data(
        seller=seller,
        start_date=start_date,
        end_date=end_date,
        asins=asins,
        graph_data_type=graph_data_type,
    ), get_graph_data_for_total_sales_data(
        seller=seller,
        start_date=prev_start_date,
        end_date=prev_end_date,
        asins=asins,
        graph_data_type=graph_data_type,
    )


def get_search_query_brand_report(*, user_id: int, amazon_seller_id: str, start_date: str, end_date: str) -> Dict:
    logger.info(f"{user_id=}, {amazon_seller_id=}, {start_date=}, {end_date=}")
    start_date = dt.convert_str_to_date(date_str=start_date)
    end_date = dt.convert_str_to_date(date_str=end_date)
    seller = get_seller_by_user_id(user_id=user_id, amazon_seller_id=amazon_seller_id)
    if not seller:
        raise ServiceException(f"seller does not exist {amazon_seller_id=}, {user_id=}")


def get_product_analysis(
    *,
    user_id: int,
    amazon_seller_id: str,
    start_date: str,
    end_date: str,
    asins: Optional[List[str]] = None,
) -> Dict:
    logger.info(f"{user_id=}, {amazon_seller_id=}, {start_date=}, {end_date=}")
    start_date = dt.convert_str_to_date(date_str=start_date)
    end_date = dt.convert_str_to_date(date_str=end_date)
    seller = get_seller_by_user_id(user_id=user_id, amazon_seller_id=amazon_seller_id)
    if not seller:
        raise ServiceException(f"seller does not exist {amazon_seller_id=}, {user_id=}")
    total_sales_data = get_total_sales(seller=seller, start_date=start_date, end_date=end_date, asins=asins)
    total_traffic_data = get_total_traffic(seller=seller, start_date=start_date, end_date=end_date, asins=asins)
    ads_sales_data = get_ads_sales(seller=seller, start_date=start_date, end_date=end_date, asins=asins)
    data = aggregate_data_by_asin(total_sales_data=total_sales_data, total_traffic_data=total_traffic_data, ads_sales_data=ads_sales_data)
    return data


def aggregate_data_by_asin(*, total_sales_data: List[Dict], total_traffic_data: List[Dict], ads_sales_data: List[Dict]) -> Dict:
    asin_wise_sales = defaultdict(lambda:defaultdict(int))
    asin_wise_traffic = defaultdict(lambda:defaultdict(int))
    asin_wise_ads_sales = defaultdict(lambda:defaultdict(int))
    ads_asin_to_campaigns = defaultdict(list)
    result = {}
    campaign_id_to_campaign_data = defaultdict(lambda:defaultdict(int))
    for data in ads_sales_data:
        sales = data["sales"]
        spend = data["spend"]
        clicks = data["clicks"]
        impressions = data["impressions"]
        asin_data = asin_wise_ads_sales[data["asin"]]
        asin_data["sales"] += sales
        asin_data["spend"] += spend
        asin_data["clicks"] += clicks
        asin_data["impressions"] += impressions
        asin_data["ctr"] = round(100 * asin_data["clicks"] / asin_data["impressions"], 2) if asin_data["impressions"] else 0
        asin_data["roas"] = round(asin_data["sales"] / asin_data["spend"], 2) if asin_data["spend"] else 0
        asin_data["acos"] = round(100 * asin_data["spend"] / asin_data["sales"], 2) if asin_data["sales"] else 0
        asin_wise_ads_sales[data["asin"]] = asin_data

        campaign_name = data["campaign_name"]
        campaign_id = data["campaign_id"]
        ad_group_name = data["ad_group_name"]
        ad_group_id = data["ad_group_id"]
        campaign_type = data["campaign_type"]

        # keep the map of asin to campaign ids
        ads_asin_to_campaigns[data["asin"]].append(campaign_id)
        # keep the map of campaign id to campaign data and ad groups
        campaign_data = campaign_id_to_campaign_data[campaign_id]
        campaign_data["sales"] += sales
        campaign_data["spend"] += spend
        campaign_data["clicks"] += clicks
        campaign_data["impressions"] += impressions
        campaign_data["ctr"] = round(100 * campaign_data["clicks"] / campaign_data["impressions"], 2) if campaign_data["impressions"] else 0
        campaign_data["roas"] = round(campaign_data["sales"] / campaign_data["spend"], 2) if campaign_data["spend"] else 0
        campaign_data["acos"] = round(100 * campaign_data["spend"] / campaign_data["sales"], 2) if campaign_data["sales"] else 0
        campaign_data["campaign_name"] = campaign_name
        campaign_data["campaign_id"] = campaign_id
        campaign_data["campaign_type"] = campaign_type

        if not campaign_data.get("ad_groups", None):
            campaign_data["ad_groups"] = {}

        ad_group_data = campaign_data["ad_groups"].get(ad_group_id, defaultdict(int))
        ad_group_data["sales"] += sales
        ad_group_data["spend"] += spend
        ad_group_data["clicks"] += clicks
        ad_group_data["impressions"] += impressions
        ad_group_data["ctr"] = round(100 * ad_group_data["clicks"] / ad_group_data["impressions"], 2) if ad_group_data["impressions"] else 0
        ad_group_data["roas"] = round(ad_group_data["sales"] / ad_group_data["spend"], 2) if ad_group_data["spend"] else 0
        ad_group_data["acos"] = round(100 * ad_group_data["spend"] / ad_group_data["sales"], 2) if ad_group_data["sales"] else 0
        ad_group_data["ad_group_name"] = ad_group_name
        ad_group_data["ad_group_id"] = ad_group_id
        campaign_data["ad_groups"][ad_group_id] = ad_group_data
        campaign_id_to_campaign_data[campaign_id] = campaign_data

    for data in total_traffic_data:
        asin_data = asin_wise_traffic[data["child_asin"]]
        asin_data["total_sessions"] += data["total_sessions"]
        asin_wise_traffic[data["child_asin"]] = asin_data
    for data in total_sales_data:
        asin_data = asin_wise_sales[data["child_asin"]]
        asin_data["sales"] += data["sales"]
        asin_data["orders"] += data["orders"]
        asin_data["units_ordered"] += data["units_ordered"]
        asin_wise_sales[data["child_asin"]] = asin_data
    
    for asin, data in asin_wise_sales.items():
        campaigns = ads_asin_to_campaigns.get(asin, [])
        campaign_data = []
        for campaign_id in campaigns:
            campaign_data.append(campaign_id_to_campaign_data[campaign_id])
        result[asin] = {
            "total_sales": int(data["sales"]),
            "total_ads_sales": int(asin_wise_ads_sales[asin]["sales"]),
            "total_ads_spend": int(asin_wise_ads_sales[asin]["spend"]),
            "total_orders": int(data["orders"]),
            "total_units_ordered": int(data["units_ordered"]),
            "total_sessions": asin_wise_traffic[asin]["total_sessions"],
            "total_clicks": asin_wise_ads_sales[asin]["clicks"],
            "total_impressions": asin_wise_ads_sales[asin]["impressions"],
            "ctr": asin_wise_ads_sales[asin]["ctr"],
            "roas": asin_wise_ads_sales[asin]["roas"],
            "acos": asin_wise_ads_sales[asin]["acos"],
            "tacos": round(100 * asin_wise_ads_sales[asin]["spend"] / data["sales"], 2) if data["sales"] else 0,
            "campaigns": campaign_data,
        }
    return result
