from typing import Dict, List

from django.db.models import QuerySet
from django.db.models.manager import BaseManager
from amazon.models import Seller, SellerCentralSale, SellerCentralTraffic, RegionDetail
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


def process_total_and_sales_data(*, total_sales: List[Dict], ads_sale: List[Dict], traffic_data: List[Dict]) -> Dict:
    total_sales_data = defaultdict(
        total_revenue=0,
        ads_revenue=0,
        organic_revenue=0,
        total_orders=0,
        ad_orders=0,
        organic_orders=0,
        total_units=0,
        total_aov=0,
        ads_spend=0,
        tacos=0,
        ads_roas=0,
        total_roas=0,
        acos=0,
        impressions=0,
        clicks=0,
        cost_per_unit=0,
        total_traffic=0,
        ad_traffic=0,
        organic_traffic=0,
    )
    # TODO: here also need to add cpm rpc cpo ctr CR% CPA
    # traffice are sessions in seller central and clicks in ads
    # conversion rate order/sessions
    # purchase = ad_order
    # ROAS = sales/spend
    # ACOS = spend/sales
    # SKIP CPA, CPM
    # CTR = clicks/impression
    # CPO = cost per order spend/total orders
    # cost per unit spend/total units
    for traffic in traffic_data:
        total_sales_data["total_traffic"] += traffic["browser_sessions"] + traffic["mobile_app_sessions"]

    for sale in total_sales:
        total_sales_data["total_revenue"] += sale["ordered_product_sales"]
        total_sales_data["total_orders"] += sale["items_ordered"]
        total_sales_data["total_units"] += sale["units_ordered"]

    for sale in ads_sale:
        total_sales_data["ads_revenue"] += sale["sales"]
        total_sales_data["ads_spend"] += sale["spend"]
        total_sales_data["impressions"] += sale["impressions"]
        total_sales_data["clicks"] += sale["clicks"]
        total_sales_data["cpc"] += sale["cpc"]
        total_sales_data["ad_orders"] += sale["orders"]
        total_sales_data["ad_traffic"] += sale["clicks"]

    total_sales_data["organic_orders"] = total_sales_data["total_orders"] - total_sales_data["ad_orders"]
    total_sales_data["organic_traffic"] = total_sales_data["total_traffic"] - total_sales_data["ad_traffic"]
    total_sales_data["organic_revenue"] = total_sales_data["total_revenue"] - total_sales_data["ads_revenue"]

    # calculate AOV
    if total_sales_data["total_orders"]:
        total_sales_data["total_aov"] = int(total_sales_data["total_revenue"] / total_sales_data["total_orders"])
    if total_sales_data["ad_orders"]:
        total_sales_data["ad_aov"] = int(total_sales_data["ads_revenue"] / total_sales_data["ad_orders"])
    if total_sales_data["organic_orders"]:
        total_sales_data["organic_aov"] = int(total_sales_data["organic_revenue"] / total_sales_data["organic_orders"])

    # Calculate conversion rate
    if total_sales_data["total_traffic"]:
        total_sales_data["total_cr"] = int(total_sales_data["total_orders"] / total_sales_data["total_traffic"])
    if total_sales_data["ad_traffic"]:
        total_sales_data["ad_cr"] = int(total_sales_data["ad_orders"] / total_sales_data["ad_traffic"])
    if total_sales_data["organic_traffic"]:
        total_sales_data["organic_cr"] = int(total_sales_data["organic_orders"] / total_sales_data["organic_traffic"])

    # Calculate ROAS
    if total_sales_data["ads_spend"]:
        total_sales_data["ads_roas"] = int(total_sales_data["ads_revenue"] / total_sales_data["ads_spend"])
        total_sales_data["total_roas"] = int(total_sales_data["total_revenue"] / total_sales_data["ads_spend"])

    # calculate ACOS
    if total_sales_data["total_revenue"]:
        total_sales_data["tacos"] = int(total_sales_data["ads_spend"] / total_sales_data["total_revenue"])  # confirm it first
    if total_sales_data["ads_revenue"]:
        total_sales_data["acos"] = int(total_sales_data["ads_spend"] / total_sales_data["ads_revenue"])  # confirm it first

    # calcuate cost per unit
    if total_sales_data["total_units"]:
        total_sales_data["cost_per_unit"] = int(total_sales_data["ads_spend"] / total_sales_data["total_units"])

    # calculate CTR
    if total_sales_data["impressions"]:
        total_sales_data["ctr"] = int(total_sales_data["clicks"] / total_sales_data["impressions"])

    # calculate cost per order
    if total_sales_data["total_orders"]:
        total_sales_data["cpo"] = int(total_sales_data["ads_spend"] / total_sales_data["total_orders"])

    # calculate average cost per click
    if ads_sale:
        total_sales_data["cpc"] = float(total_sales_data["cpc"] / len(ads_sale))
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


def serialize_amazon_profile_account(*, profile: Seller):
    return {
        "amazon_seller_id": profile.amazon_seller_id,
        "marketplace_id": profile.marketplace_id,
        "store_name": profile.store_name,
        "country_code": profile.country_code,
    }
