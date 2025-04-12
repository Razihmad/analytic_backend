# Standard Library
import logging
import datetime
from typing import List, Optional, Dict

# Third Party Stuff
from django.contrib.auth.models import User

# Local
from amazon_ads.constants import GraphDataType
import utils.datetime as dt
from amazon.models import Seller
from amazon_ads.selectors import get_ads_profile_by_user_and_seller_id, get_ads_sales_data
from amazon_ads.serializers import group_ads_impression_by_date, group_ads_orders_by_date, group_ads_sales_data_by_date, group_ads_traffic_by_date, serialize_ads_sales_data
from amazon_ads.tasks import (
    start_fetching_ad_sales_data_by_campaign, start_fetching_amazon_ads_by_date_range, start_fetching_amazon_ads_campaign_by_date_range, start_fetcing_ad_sales_data_by_asin
)
from base.exception import ServiceException
from amazon_ads.models import AmazonAdsSaleAsin, AmazonAdsSaleCampaign

logger = logging.getLogger(__name__)


def start_fetching_amazon_ads_data(*, amazon_seller_id: str, user: User):
    if not amazon_seller_id:
        raise ServiceException("amazon_seller_id is required")
    ads_profile = get_ads_profile_by_user_and_seller_id(user_id=user.pk, amazon_seller_id=amazon_seller_id)
    if not ads_profile:
        raise ServiceException("ads profile does not exists")
    start_fetcing_ad_sales_data_by_asin.apply_async(args=[
        ads_profile.country_code, user.pk, amazon_seller_id, ads_profile.profile_id, ads_profile.pk
    ], queue="process_report")
    start_fetching_ad_sales_data_by_campaign.apply_async(args=[
        ads_profile.country_code, user.pk, amazon_seller_id, ads_profile.profile_id, ads_profile.pk
    ], queue="process_report")


def prepare_data_to_bulk_upsert(
    *, data: List[Dict], ad_account_id: int, campaign_type: str
) -> List[AmazonAdsSaleAsin]:
    bulk_upsert_data = []
    for item in data:
        cpc = 0
        if item.get("costPerClick"):
            cpc = item["costPerClick"]
        elif item["clicks"]:
            cpc = float(item["cost"] / item["clicks"])
        bulk_upsert_data.append(
            AmazonAdsSaleAsin(
                amazon_ads_id=ad_account_id,
                asin=item["advertisedAsin"],
                sales_date=item["date"],
                sales=item["sales7d"],
                units_sold=item["unitsSoldClicks7d"],
                cost=item["cost"],
                impressions=item["impressions"],
                clicks=item["clicks"],
                spend=item["cost"],
                orders=item["purchases7d"],
                cpc=cpc,
                campaign_type=campaign_type
            )
        )
    return bulk_upsert_data


def prepare_campaing_level_data_for_upsert(*, data: List[Dict], ad_account_id: int, campaign_type: str) -> List[AmazonAdsSaleCampaign]:
    bulk_upsert_data = []
    for item in data:
        cpc = 0
        if item.get("costPerClick"):
            cpc = item["costPerClick"]
        elif item["clicks"]:
            cpc = float(item["cost"] / item["clicks"])
        bulk_upsert_data.append(
            AmazonAdsSaleCampaign(
                amazon_ads_id=ad_account_id,
                campaign_name=item["campaignName"],
                sales_date=item["date"],
                sales=item["sales14d"],
                units_sold=item["unitsSoldClicks14d"],
                cost=item["cost"],
                impressions=item["impressions"],
                clicks=item["clicks"],
                spend=item["cost"],
                cpc=cpc,
                campaign_bidding_strategy=item.get("campaignBiddingStrategy"),
                campaign_status=item["campaignStatus"],
                orders=item["purchases14d"],
                campaign_type=campaign_type,
            )
        )
    return bulk_upsert_data


def get_ads_sales(*, ads_profile: Optional[Seller], start_date: datetime.date, end_date: datetime.date, asins: Optional[List[str]] = None) -> List[Dict]:
    if not ads_profile:
        return []
    logger.info(f"{ads_profile.user_id=}, {ads_profile.amazon_seller_id=}, {start_date=}, {end_date=}, {asins=}")
    ads_sales = get_ads_sales_data(profile=ads_profile, start_date=start_date, end_date=end_date, asins=asins)
    ads_sales_data = serialize_ads_sales_data(sales=ads_sales)
    return ads_sales_data


def verify_and_get_ads_profile(*, user_id: int, amazon_seller_id: Optional[str]) -> Optional[Seller]:
    if not amazon_seller_id:
        return
    ads_profile = get_ads_profile_by_user_and_seller_id(user_id=user_id, amazon_seller_id=amazon_seller_id)
    return ads_profile


def validate_incoming_data(*, amazon_seller_id: str, start_date: str, end_date: str):
    from utils.validators import FetchData
    return FetchData(start_date=start_date, end_date=end_date, amazon_seller_id=amazon_seller_id)


def fetch_ads_data_by_date(*, user_id: int, amazon_seller_id: str, start_date: str, end_date: str):
    ads_profile = get_ads_profile_by_user_and_seller_id(user_id=user_id, amazon_seller_id=amazon_seller_id)
    if not ads_profile:
        raise ServiceException(f"no ads profile for {user_id=}, {amazon_seller_id=}")
    logger.info(f"{ads_profile=}")
    country_code = ads_profile.country_code
    start_fetching_amazon_ads_by_date_range.apply_async(
        args=[
            amazon_seller_id,
            start_date,
            end_date,
            country_code,
            ads_profile.profile_id,
            ads_profile.id,
            user_id,
        ],
        queue="process_ads_report"
    )
    start_fetching_amazon_ads_campaign_by_date_range.apply_async(
        args=[
            amazon_seller_id,
            start_date,
            end_date,
            country_code,
            ads_profile.profile_id,
            ads_profile.id,
            user_id,
        ],
        queue="process_ads_report"
    )


def get_ads_data_for_graph(*, seller: Seller, graph_data_type: str, start_date: str, end_date: str, asins: Optional[List[str]]):
    logger.info(f"{seller=}, {start_date=}, {end_date=}, {asins=}, {graph_data_type=}")
    start_date = dt.convert_str_to_date(date_str=start_date)
    end_date = dt.convert_str_to_date(date_str=end_date)
    field = GraphDataType[graph_data_type]
    ads_sales = get_ads_sales_data(profile=seller, start_date=start_date, end_date=end_date, asins=asins, fields=[field.value])
    if graph_data_type == GraphDataType.REVENUE.name:
        return group_ads_sales_data_by_date(sales_data=ads_sales)
    if graph_data_type == GraphDataType.ORDERS.name:
        return group_ads_orders_by_date(orders_data=ads_sales)
    if graph_data_type in [GraphDataType.TRAFFIC.name, GraphDataType.CLICKS.name]:
        return group_ads_traffic_by_date(traffic_data=ads_sales)
    if graph_data_type == GraphDataType.IMPRESSIONS.name:
        return group_ads_impression_by_date(ads_data=ads_sales)
