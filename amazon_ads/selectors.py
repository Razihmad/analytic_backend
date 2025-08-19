import datetime
from typing import Dict, List, Optional

from django.db.models import Case, ExpressionWrapper, FloatField, F, QuerySet, Q, Value, When

from amazon_ads.models import AmazonAdsSaleAsin, AmazonAdsSaleCampaign, SearchTerm, Targeting
from amazon.models import Seller


def get_ads_profile_by_user_and_seller_id(*, user_id: int, amazon_seller_id: str) -> Optional[Seller]:
    return Seller.objects.filter(user_id=user_id, amazon_seller_id=amazon_seller_id).first()


def bulk_upsert_amazon_ads_sales(*, data: List[AmazonAdsSaleAsin]):
    return AmazonAdsSaleAsin.objects.bulk_create(data, update_conflicts=True, update_fields=[
        "sales", "units_sold", "cost", "impressions", "clicks", "spend", "orders", "cpc"
    ], unique_fields=['amazon_ads', 'asin', 'sales_date', "campaign_type", "campaign_id", "ad_group_id"])


def bulk_upsert_amazon_ads_campaign_sales(*, data: List[AmazonAdsSaleCampaign]):
    return AmazonAdsSaleCampaign.objects.bulk_create(data, update_conflicts=True, update_fields=[
        "sales", "impressions", "clicks", "spend", "cpc", "orders", "campaign_id"
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
    *, seller_id: int, start_date: datetime.date, end_date: datetime.date, campaign_name: Optional[str] = None, campaign_type: Optional[List[str]] = None
) ->  QuerySet[AmazonAdsSaleCampaign]:
    base_filter = Q(amazon_ads_id=seller_id, sales_date__range=(start_date, end_date))
    if campaign_name:
        base_filter &= Q(campaign_name__icontains=campaign_name)
    if campaign_type:
        base_filter &= Q(campaign_type__in=campaign_type)
    return AmazonAdsSaleCampaign.objects.filter(base_filter)


def bulk_upsert_search_term_report_data(*, data: List[SearchTerm]):
    return SearchTerm.objects.bulk_create(data, ignore_conflicts=True, batch_size=500)


def bulk_upsert_targeting_report_data(*, data: List[Targeting]):
    return Targeting.objects.bulk_create(data, update_conflicts=True, update_fields=[
        "sales", "impressions", "clicks", "cost", "orders", "campaign_id", "campaign_status", "keyword_status", "top_of_search_is"
    ], unique_fields=['seller', 'targeting', 'keyword_id', 'campaign_id', 'targeting_date', 'campaign_type'])


def get_serach_term_report_data(
    *,
    seller_id: int,
    start_date: datetime.date,
    end_date: datetime.date,
    search_term: Optional[str] = None,
    campaign_name: Optional[str] = None,
    keyword: Optional[str] = None,
    ad_group_name: Optional[str] = None,
    match_type: Optional[str] = None,
    query_params: Optional[Dict] = None,
):
    base_filter = Q(seller_id=seller_id, search_term_date__range=[start_date, end_date])
    if query_params:
        for param, value in query_params.items():
            if "__" in param:
                field, lookup = param.split("__", 1)
            else:
                field, lookup = param, "exact"
            lookup_exp = f"{field}__{lookup}"
            base_filter &= Q(**{lookup_exp: value})

    if search_term:
        base_filter &= Q(search_term__icontains=search_term)
    if campaign_name:
        base_filter &= Q(campaign_name__icontains=campaign_name)
    if keyword:
        base_filter &= Q(keyword__icontains=keyword)
    if ad_group_name:
        base_filter &= Q(ad_group_name__icontains=ad_group_name)
    if match_type:
        base_filter &= Q(match_type=match_type)
    return SearchTerm.objects.annotate(
        acos=Case(
            When(sales=0, then=Value(0.0)),
            default=ExpressionWrapper(F("cost") / F("sales") * 100, output_field=FloatField()),
            output_field=FloatField()
        ),
        roas=Case(
            When(cost=0, then=Value(0.0)),
            default=ExpressionWrapper(F("sales") / F("cost"), output_field=FloatField()),
            output_field=FloatField()
        ),
        cvr=Case(
            When(clicks=0, then=Value(0.0)),
            default=ExpressionWrapper(F("orders") / F("clicks") * 100, output_field=FloatField()),
            output_field=FloatField()
        ),
        cpc=Case(
            When(clicks=0, then=Value(0.0)),
            default=ExpressionWrapper(F("cost") / F("clicks"), output_field=FloatField()),
            output_field=FloatField()
        ),
        ctr=Case(
            When(impressions=0, then=Value(0.0)),
            default=ExpressionWrapper(F("clicks") / F("impressions") * 100, output_field=FloatField()),
            output_field=FloatField()
        ),
    ).filter(base_filter)


def get_asins_by_camapagin_ids(*, campaign_ids: set[str], start_date: datetime.date, end_date: datetime.date) -> QuerySet[AmazonAdsSaleAsin]:
    return AmazonAdsSaleAsin.objects.filter(
        campaign_id__in=campaign_ids, sales_date__range=[start_date, end_date]
    ).only("asin", "campaign_id", "campaign_name")


def get_targeting_report_data(
    *,
    seller_id: int,
    start_date: datetime.date,
    end_date: datetime.date,
    campaign_name: Optional[str] = None,
    ad_group_name: Optional[str] = None,
    query_params: Optional[Dict] = None,
    match_type: Optional[str] = None,
    targeting: Optional[str] = None,
):
    base_filter = Q(seller_id=seller_id, targeting_date__range=[start_date, end_date])
    if query_params:
        for param, value in query_params.items():
            if "__" in param:
                field, lookup = param.split("__", 1)
            else:
                field, lookup = param, "exact"
            lookup_exp = f"{field}__{lookup}"
            base_filter &= Q(**{lookup_exp: value})

    if campaign_name:
        base_filter &= Q(campaign_name__icontains=campaign_name)
    if targeting:
        base_filter &= Q(targeting__icontains=targeting)
    if ad_group_name:
        base_filter &= Q(ad_group_name__icontains=ad_group_name)
    if match_type:
        base_filter &= Q(match_type=match_type)
    return Targeting.objects.annotate(
        acos=Case(
            When(sales=0, then=Value(0.0)),
            default=ExpressionWrapper(F("cost") / F("sales") * 100, output_field=FloatField()),
            output_field=FloatField()
        ),
        roas=Case(
            When(cost=0, then=Value(0.0)),
            default=ExpressionWrapper(F("sales") / F("cost"), output_field=FloatField()),
            output_field=FloatField()
        ),
        cvr=Case(
            When(clicks=0, then=Value(0.0)),
            default=ExpressionWrapper(F("orders") / F("clicks") * 100, output_field=FloatField()),
            output_field=FloatField()
        ),
        cpc=Case(
            When(clicks=0, then=Value(0.0)),
            default=ExpressionWrapper(F("cost") / F("clicks"), output_field=FloatField()),
            output_field=FloatField()
        ),
        ctr=Case(
            When(impressions=0, then=Value(0.0)),
            default=ExpressionWrapper(F("clicks") / F("impressions") * 100, output_field=FloatField()),
            output_field=FloatField()
        ),
    ).filter(base_filter).order_by("-created_at")
