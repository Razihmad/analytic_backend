import datetime
from typing import List, Optional

from django.db.models import QuerySet

from amazon_ads.models import AmazonAdsSaleAsin, AmazonAdsSaleCampaign
from amazon.models import Seller


def get_ads_profile_by_user_and_seller_id(*, user_id: int, amazon_seller_id: str) -> Optional[Seller]:
    return Seller.objects.filter(user_id=user_id, amazon_seller_id=amazon_seller_id).first()


def bulk_upsert_amazon_ads_sales(*, data: List[AmazonAdsSaleAsin]):
    return AmazonAdsSaleAsin.objects.bulk_create(data, ignore_conflicts=True)


def bulk_upsert_amazon_ads_campaign_sales(*, data: List[AmazonAdsSaleCampaign]):
    return AmazonAdsSaleCampaign.objects.bulk_create(data, ignore_conflicts=True)


def get_ads_sales_data(*, profile: Seller, start_date: datetime.date, end_date: datetime.date) -> QuerySet[AmazonAdsSaleAsin]:
    return AmazonAdsSaleAsin.objects.filter(amazon_ads=profile, sales_date__gte=start_date, sales_date__lte=end_date)
