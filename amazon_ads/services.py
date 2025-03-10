from django.contrib.auth.models import User

from amazon_ads.selectors import get_ads_profile_by_user_and_seller_id
from amazon_ads.tasks import (
    start_fetching_ad_sales_data_by_campaign, start_fetcing_ad_sales_data_by_asin
)
from base.exception import ServiceException
from typing import List
from typing import Dict
from amazon_ads.models import AmazonAdsSaleAsin, AmazonAdsSaleCampaign


def start_fetching_amazon_ads_data(*, amazon_seller_id: str, user: User):
    if not amazon_seller_id:
        raise ServiceException("amazon_seller_id is required")
    ads_profile = get_ads_profile_by_user_and_seller_id(user_id=user.pk, amazon_seller_id=amazon_seller_id)
    if not ads_profile:
        raise ServiceException("ads profile does not exists")
    start_fetcing_ad_sales_data_by_asin.apply_async(args=[
        ads_profile.country_code, user.pk, amazon_seller_id, ads_profile.profile_id, ads_profile.pk
    ])
    start_fetching_ad_sales_data_by_campaign.apply_async(args=[
        ads_profile.country_code, user.pk, amazon_seller_id, ads_profile.profile_id, ads_profile.pk
    ])


def prepare_data_to_bulk_upsert(*, data: List[Dict], user_id: int, ad_account_id: int) -> List[AmazonAdsSaleAsin]:
    bulk_upsert_data = []
    for item in data:
        bulk_upsert_data.append(
            AmazonAdsSaleAsin(
                user_id=user_id,
                amazon_ads_id=ad_account_id,
                asin=item["advertisedAsin"],
                sales_date=item["date"],
                sales=item["sales7d"] + item["sales1d"] + item["sales14d"],
                units_sold=item["unitsSoldClicks1d"] + item["unitsSoldClicks7d"] + item["unitsSoldClicks14d"],
                cost=item["cost"],
                impressions=item["impressions"],
                clicks=item["clicks"],
                spend=item["spend"],
                cpc=item["costPerClick"],
            )
        )
    return bulk_upsert_data


def prepare_campaing_level_data_for_upsert(*, data: List[Dict], user_id: int, ad_account_id: int) -> List[AmazonAdsSaleCampaign]:
    bulk_upsert_data = []
    for item in data:
        bulk_upsert_data.append(
            AmazonAdsSaleCampaign(
                user_id=user_id,
                amazon_ads_id=ad_account_id,
                campaign_name=item["campaignName"],
                campaign_id=item["campaignId"],
                sales_date=item["date"],
                sales=item["sales7d"] + item["sales1d"] + item["sales14d"],
                units_sold=item["unitsSoldClicks1d"] + item["unitsSoldClicks7d"] + item["unitsSoldClicks14d"],
                cost=item["cost"],
                impressions=item["impressions"],
                clicks=item["clicks"],
                spend=item["spend"],
                cpc=item["costPerClick"],
                campaign_bidding_strategy=item["campaignBiddingStrategy"],
                campaign_status=item["campaignStatus"],
            )
        )
    return bulk_upsert_data
