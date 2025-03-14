from typing import Dict, List

from django.db.models import QuerySet
from django.db.models.manager import BaseManager
from amazon.models import SellerCentralSale, SellerCentralTraffic, RegionDetail
from collections import defaultdict


def serialize_seller_central_sales(*, sales: QuerySet[SellerCentralSale]) -> List[Dict]:
    result = []
    for sale in sales:
        result.append(
            {
                "child_asin": sale.child_asin,
                "parent_asin": sale.parent_asin,
                "sales_date": sale.sales_date,
                "units_ordered": sale.units_ordered,
                "ordered_product_sales": sale.ordered_product_sales,
                "items_ordered": sale.items_ordered,
            }
        )
    return result


def serialize_seller_central_traffic(*, traffics: QuerySet[SellerCentralTraffic]) -> List[Dict]:
    result = []
    for traffic in traffics:
        result.append(
            {
                "child_asin": traffic.child_asin,
                "sku": traffic.sku,
                "sessions_date": traffic.sessions_date,
                "browser_sessions": traffic.browser_sessions,
                "mobile_app_sessions": traffic.mobile_app_sessions,
                "browser_page_views": traffic.browser_page_views,
                "mobile_app_page_views": traffic.mobile_app_page_views,
                "unit_sessions_percentage": traffic.unit_sessions_percentage
            }
        )
    return result


def process_total_and_sales_data(*, total_sales: List[Dict], ads_sale: List[Dict]) -> Dict:
    total_sales_data = defaultdict(
        total_revenue=0,
        ads_revenue=0,
        organic_revenue=0,
        total_orders=0,
        total_units=0,
        ads_unit=0,
        organic_unit=0,
        total_aov=0,
        ads_spend=0,
        tacos=0,
        ads_roas=0,
        total_roas=0,
        acos=0,
    )

    for sale in total_sales:
        total_sales_data["total_revenue"] += sale["ordered_product_sales"]
        total_sales_data["total_orders"] += sale["items_ordered"]
        total_sales_data["total_units"] += sale["units_ordered"]

    total_sales_data["organic_revenue"] = total_sales_data["total_revenue"] - total_sales_data["ads_revenue"]
    if total_sales_data["total_orders"] != 0:
        total_sales_data["total_aov"] = int(total_sales_data["total_revenue"] / total_sales_data["total_orders"])

    for sale in ads_sale:
        total_sales_data["ads_revenue"] += sale["sales"]
        total_sales_data["ads_spend"] += sale["spend"]

    if total_sales_data["total_revenue"]:
        total_sales_data["tacos"] = int(total_sales_data["ads_spend"] / total_sales_data["total_revenue"])  # confirm it first
    if total_sales_data["ads_revenue"]:
        total_sales_data["acos"] = int(total_sales_data["ads_spend"] / total_sales_data["ads_revenue"])  # confirm it first
    if total_sales_data["ads_spend"]:
        total_sales_data["ads_roas"] = int(total_sales_data["ads_revenue"] / total_sales_data["ads_spend"])
        total_sales_data["total_roas"] = int(total_sales_data["total_revenue"] / total_sales_data["ads_spend"])

    return total_sales_data


def serialize_regions_details(*, regions: BaseManager[RegionDetail]) -> List[Dict]:
    serialized_regions = []
    for region in regions:
        serialized_regions.append(
            {
                "country": region.country,
                "country_code": region.country_code,
                "region": region.region,
                "marketplce_id": region.marketplace_id
            }
        )
    return serialized_regions
