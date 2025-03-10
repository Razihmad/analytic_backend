from typing import List, Optional
from .models import AmazonAdsAccount, AmazonAdsSaleAsin, AmazonAdsSaleCampaign


def get_ads_profile_by_user_and_seller_id(*, user_id: int, amazon_seller_id: str) -> Optional[AmazonAdsAccount]:
    return AmazonAdsAccount.objects.filter(user_id=user_id, amazon_seller_id=amazon_seller_id).first()


def bulk_upsert_amazon_ads_sales(*, data: List[AmazonAdsSaleAsin]):
    return AmazonAdsSaleAsin.objects.bulk_create(data, ignore_conflicts=True)


def bulk_upsert_amazon_ads_campaign_sales(*, data: List[AmazonAdsSaleCampaign]):
    return AmazonAdsSaleCampaign.objects.bulk_create(data, ignore_conflicts=True)
