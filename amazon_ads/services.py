# Standard Library
from collections import defaultdict
import logging
import datetime
from typing import List, Optional, Dict, Tuple

# Third Party Stuff
import pandas as pd
from django.contrib.auth.models import User
from django.db.models import QuerySet

# Local
from amazon_ads.constants import GraphDataType
import utils.datetime as dt
from amazon.models import Seller
from amazon_ads.selectors import bulk_upsert_amazon_ads_campaign_sales, get_ads_profile_by_user_and_seller_id, get_ads_sales_data, get_asins_by_camapagin_ids, get_campaign_sales_report, get_serach_term_report_data
from amazon_ads.serializers import group_ads_sales_data_by_date, serialize_ads_sales_data, serialize_campaign_sales_report, serialize_search_term_report
from amazon_ads.tasks import (
    start_fetching_ad_sales_data_by_campaign, start_fetching_amazon_ads_by_date_range, start_fetching_amazon_ads_campaign_by_date_range, start_fetching_search_term_report, start_fetcing_ad_sales_data_by_asin
)
from base.exception import ServiceException
from amazon_ads.models import AmazonAdsSaleAsin, AmazonAdsSaleCampaign, SearchTerm

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
        if item["clicks"]:
            cpc = float(item["cost"] / item["clicks"])
        bulk_upsert_data.append(
            AmazonAdsSaleAsin(
                amazon_ads_id=ad_account_id,
                asin=item["asin"],
                sales_date=item["sales_date"],
                sales=item["sales"],
                units_sold=item["units_sold"],
                cost=item["cost"],
                impressions=item["impressions"],
                clicks=item["clicks"],
                spend=item["cost"],
                orders=item["orders"],
                cpc=cpc,
                campaign_type=campaign_type,
                campaign_name=item["campaign_name"],
                campaign_id=item["campaign_id"]
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


def get_ads_sales(*, ads_profile: Optional[Seller], start_date: datetime.date, end_date: datetime.date, asins: Optional[List[str]] = None, fields: Optional[List[str]] = None) -> List[Dict]:
    if not ads_profile:
        return []
    logger.info(f"{ads_profile.user_id=}, {ads_profile.amazon_seller_id=}, {start_date=}, {end_date=}, {asins=}")
    ads_sales = get_ads_sales_data(profile=ads_profile, start_date=start_date, end_date=end_date, asins=asins, fields=fields)
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
    start_fetching_search_term_report.apply_async(
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


def get_ads_data_for_graph(*, seller: Seller, graph_data_type: str, start_date: datetime.date, end_date: datetime.date, asins: Optional[List[str]]):
    logger.info(f"{seller=}, {start_date=}, {end_date=}, {asins=}, {graph_data_type=}")
    field = GraphDataType[graph_data_type]
    field = field.value
    if graph_data_type == GraphDataType.TRAFFIC.name:
        field = "clicks"
    ads_sales = get_ads_sales_data(profile=seller, start_date=start_date, end_date=end_date, asins=asins, fields=[field])
    return group_ads_sales_data_by_date(ads_sales_data=ads_sales, field=field)


def process_campaign_sb_report_file(*, file, amazon_seller_id: str, user_id: int, sales_date: str):
    sales_date = dt.convert_str_to_date(date_str=sales_date)
    df = pd.read_csv(file)
    df = df.rename(
        columns={
            "Campaigns": "campaign_name",
            "Campaign bidding strategy": "campaign_bidding_strategy",
            "Impressions": "impressions",
            "Clicks": "clicks",
            "Spend(INR)": "spend",
            "CPC(INR)": "cpc",
            "Orders": "orders",
            "Sales(INR)": "sales",
            "Status": "campaign_status"
        }
    )
    df = df.where(pd.notnull(df), None)
    seller = get_ads_profile_by_user_and_seller_id(user_id=user_id, amazon_seller_id=amazon_seller_id)
    campaign_sales = []
    for _, row in df.iterrows():
        camapgin_sale = AmazonAdsSaleCampaign(
            campaign_name=row["campaign_name"],
            sales_date=sales_date,
            amazon_ads_id=seller.id,
            sales=row["sales"],
            impressions=row["impressions"],
            clicks=row["clicks"],
            spend=row["spend"],
            cpc=row["cpc"],
            campaign_bidding_strategy=row["campaign_bidding_strategy"],
            orders=row["orders"],
            campaign_status=row["campaign_status"],
            campaign_type="SPONSORED_BRAND",
        )
        campaign_sales.append(camapgin_sale)
    bulk_upsert_amazon_ads_campaign_sales(data=campaign_sales)


def get_and_serialize_campaign_report_data(*, user_id: int, amazon_seller_id: str, start_date: str, end_date: str) -> Tuple[List[Dict], Dict]:
    start_date = dt.convert_str_to_date(date_str=start_date)
    end_date = dt.convert_str_to_date(date_str=end_date)
    seller = get_ads_profile_by_user_and_seller_id(user_id=user_id, amazon_seller_id=amazon_seller_id)
    if not seller:
        raise ServiceException(f"seller does not exist {amazon_seller_id=}")
    campaign_sales = get_campaign_sales_report(seller_id=seller.id, start_date=start_date, end_date=end_date)
    return serialize_campaign_sales_report(campaign_sales=campaign_sales)


def prepare_search_term_bulk_insert(*, data: List[Dict], ad_account_id: int) -> List[SearchTerm]:
    search_terms = []
    for record in data:
        search_term = SearchTerm(
            seller_id=ad_account_id,
            **record
        )
        search_terms.append(search_term)
    return search_terms


def get_and_serialize_serach_term_report_data(
    *, user_id: int, amazon_seller_id: str, start_date: str, end_date: str
) -> List[Dict]:
    logger.info(f"{user_id=}, {amazon_seller_id=}, {start_date=}, {end_date=}")
    start_date = dt.convert_str_to_date(date_str=start_date)
    end_date = dt.convert_str_to_date(date_str=end_date)
    seller = get_ads_profile_by_user_and_seller_id(user_id=user_id, amazon_seller_id=amazon_seller_id)
    if not seller:
        raise ServiceException(f"seller does not exist {amazon_seller_id=}")
    logger.info(f"{user_id=}, {seller.id=}, {start_date=}, {end_date=}")
    search_term_data = get_serach_term_report_data(seller_id=seller.id, start_date=start_date, end_date=end_date)
    campaign_to_asins = get_asins_by_campaign_ids(search_term_data=search_term_data, start_date=start_date, end_date=end_date)

    data = serialize_search_term_report(search_terms=search_term_data, campaign_to_asins=campaign_to_asins)
    return data


def get_asins_by_campaign_ids(*, search_term_data: QuerySet[SearchTerm], start_date: datetime.date, end_date: datetime.date) -> List[Dict]:
    campaign_ids = set()
    for data in search_term_data:
        campaign_ids.add(data.campaign_id)
    asin_sales = get_asins_by_camapagin_ids(campaign_ids=campaign_ids, start_date=start_date, end_date=end_date)
    data = defaultdict(list)
    for record in asin_sales:
        data[record.campaign_id].append(record.asin)

    return data
