import datetime
from typing import List, Optional

from django.db.models import QuerySet, Q

from amazon_ads.models import AmazonAdsSaleAsin, AmazonAdsSaleCampaign, SearchTerm
from amazon.models import Seller


def get_ads_profile_by_user_and_seller_id(*, user_id: int, amazon_seller_id: str) -> Optional[Seller]:
    return Seller.objects.filter(user_id=user_id, amazon_seller_id=amazon_seller_id).first()


def bulk_upsert_amazon_ads_sales(*, data: List[AmazonAdsSaleAsin]):
    return AmazonAdsSaleAsin.objects.bulk_create(data, update_conflicts=True, update_fields=[
        "sales", "units_sold", "cost", "impressions", "clicks", "spend", "orders", "cpc"
    ], unique_fields=['amazon_ads', 'asin', 'sales_date', "campaign_type", "campaign_id"])


def bulk_upsert_amazon_ads_campaign_sales(*, data: List[AmazonAdsSaleCampaign]):
    return AmazonAdsSaleCampaign.objects.bulk_create(data, update_conflicts=True, update_fields=[
        "sales", "impressions", "clicks", "spend", "cpc", "orders"
    ], unique_fields=['amazon_ads', 'campaign_name', 'sales_date', "campaign_type"])


def get_ads_sales_data(
    *, profile: Seller, start_date: datetime.date, end_date: datetime.date, asins: Optional[List[str]], fields: Optional[List[str]]
) -> QuerySet[AmazonAdsSaleAsin]:
    base_filter = Q(amazon_ads=profile, sales_date__gte=start_date, sales_date__lte=end_date)
    if asins:
        base_filter &= Q(asin__in=asins)
    data = AmazonAdsSaleAsin.objects.filter(base_filter)
    if fields:
        return data.values("sales_date", *fields)
    return data


def get_campaign_sales_report(
    *, seller_id: int, start_date: datetime.date, end_date: datetime.date, campaign_name: Optional[str] = None, campaign_type: Optional[str] = None
) ->  QuerySet[AmazonAdsSaleCampaign]:
    base_filter = Q(amazon_ads_id=seller_id, sales_date__range=(start_date, end_date))
    if campaign_name:
        base_filter &= Q(campaign_name__icontains=campaign_name)
    if campaign_type:
        base_filter &= Q(campaign_type=campaign_type)
    return AmazonAdsSaleCampaign.objects.filter(base_filter)


def bulk_upsert_search_term_report_data(*, data: List[SearchTerm]):
    return SearchTerm.objects.bulk_create(data, ignore_conflicts=True, batch_size=500)


def get_serach_term_report_data(*, seller_id: int, start_date: datetime.date, end_date: datetime.date):
    return SearchTerm.objects.filter(seller_id=seller_id, search_term_date__range=[start_date, end_date])


def get_asins_by_camapagin_ids(*, campaign_ids: set[str], start_date: datetime.date, end_date: datetime.date) -> QuerySet[AmazonAdsSaleAsin]:
    return AmazonAdsSaleAsin.objects.filter(
        campaign_id__in=campaign_ids, sales_date__range=[start_date, end_date]
    ).only("asin", "campaign_id", "campaign_name")
