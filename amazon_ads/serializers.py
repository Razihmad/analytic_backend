

from collections import defaultdict
from typing import Dict, List
import pandas as pd
from django.db.models import QuerySet
from amazon_ads.constants import AdProduct
from amazon_ads.models import AmazonAdsSaleAsin, AmazonAdsSaleCampaign, SearchTerm


def serialize_ads_sales_data(*, sales: QuerySet[AmazonAdsSaleAsin]) -> List[Dict]:
    serialized_data = []
    for sale in sales:
        serialized_data.append(
            {
                "asin": sale.asin,
                "sales_date": sale.sales_date,
                "sales": sale.sales,
                "units_sold": sale.units_sold,
                "cost": sale.cost,
                "impressions": sale.impressions,
                "clicks": sale.clicks,
                "spend": sale.spend,
                "cpc": sale.cpc,
                "orders": sale.orders,
            }
        )
    return serialized_data


def group_ad_sales_by_asin(*, sales: List[Dict], campaign_type: str) -> List[Dict]:
    if campaign_type == AdProduct.SPONSORED_DISPLAY.value:
        return group_by_sd_ad_sales_by_asin(sales=sales)
    data = pd.DataFrame(sales)
    data = data.rename(
        columns={
            "advertisedAsin": "asin", "date": "sales_date",
            "purchases7d": "orders", "costPerClick": "cpc",
            "unitsSoldClicks7d": "units_sold", "sales7d": "sales",
            "campaignName": "campaign_name", "campaignId": "campaign_id"
        }
    )
    data.fillna(0)
    data = data.round(2)
    return data.to_dict(orient="records")


def group_by_sd_ad_sales_by_asin(sales: List[Dict]) -> List[Dict]:
    data = pd.DataFrame(sales)
    data = data.rename(
        columns={
            "purchases": "orders", "unitsSoldClicks": "units_sold",
            "promotedAsin": "asin", "campaignName": "campaign_name",
            "campaignId": "campaign_id"
        }
    )
    data.fillna(0)
    data = data.round(2)
    return data.to_dict(orient="records")


def group_ad_sales_by_campaign(*, sales: List[Dict], campaign_type: str) -> List[Dict]:
    if campaign_type in [AdProduct.SPONSORED_DISPLAY.value, AdProduct.SPONSORED_BRANDS.value]:
        return group_by_sd_ad_sales_by_campaign(sales=sales)
    data = pd.DataFrame(sales)
    data = data.groupby(["campaignName", "date"], as_index=False).agg(
        {
            "sales14d": 'sum', "impressions": "sum", "clicks": "sum", "cost": "sum",
            "costPerClick": "sum", "purchases14d": "sum", "unitsSoldClicks14d": "sum",
            "campaignStatus": "first"
        }
    )
    data = data.fillna(0)
    data = data.round(2)
    return data.to_dict(orient="records")


def group_by_sd_ad_sales_by_campaign(sales: List[Dict]) -> List[Dict]:
    data = pd.DataFrame(sales)
    data = data.rename(
        columns={"sales": "sales14d", "purchases": "purchases14d", "unitsSoldClicks": "unitsSoldClicks14d"}
    )
    data = data.groupby(["campaignName", "date"], as_index=False).agg(
        {
            "sales14d": 'sum', "impressions": "sum", "clicks": "sum", "cost": "sum",
            "purchases14d": "sum", "unitsSoldClicks14d": "sum", "campaignStatus": "first"
        }
    )
    data.fillna(0)
    data = data.round(2)
    return data.to_dict(orient="records")


def group_ads_sales_data_by_date(*, ads_sales_data: QuerySet, field: str) -> Dict:
    result = defaultdict(int)
    for data in ads_sales_data:
        result[str(data["sales_date"])] += (data[field])
    return result


def serialize_campaign_sales_report(*, campaign_sales: QuerySet[AmazonAdsSaleCampaign]) -> List[Dict]:
    result = []
    cumulative_data = defaultdict(int)
    for sale in campaign_sales:
        result.append({
            "campaign_name": sale.campaign_name,
            "status": sale.campaign_status,
            "type": sale.campaign_type,
            "sales_date": sale.sales_date,
            "sales": sale.sales,
            "impressions": sale.impressions,
            "clicks": sale.clicks,
            "spend": sale.spend,
            "cpc": sale.cpc,
            "campaign_bidding_strategy": sale.campaign_bidding_strategy,
            "orders": sale.orders,
        })
        cumulative_data["total_sales"] += sale.sales
        cumulative_data["tota_clicks"] += sale.clicks
        cumulative_data["total_impressions"] += sale.impressions
        cumulative_data["tota_spend"] += sale.spend
        cumulative_data["total_orders"] += sale.orders

    return result, cumulative_data


def serialize_search_term_report_data(*, data: List[Dict]):
    data = pd.DataFrame(data)
    data = data.rename(
        columns={
            "sales14d": 'sales', "purchases14d": "orders", "unitsSoldClicks14d": "units_sold", "keywordId": "keyword_id",
            "campaignName": "campaign_name", "campaignId": "campaign_id", "keywordBid": "keyword_bid", "adGroupName": "ad_group_name",
            "adGroupId": "ad_group_id", "keywordType": "keyword_type", "matchType": "match_type", "date": "search_term_date",
            "searchTerm": "search_term"
        }
    )
    data.fillna(0)
    data = data.round(2)
    return data.to_dict(orient="records")


def serialize_search_term_report(*, search_terms: QuerySet[SearchTerm], campaign_to_asins: Dict) -> List[Dict]:
    result = []
    for data in search_terms:
        result.append({
            "search_term": data.search_term,
            "keyword": data.keyword,
            "ad_group": data.ad_group_name,
            "sales": data.sales,
            "cost": data.cost,
            "impressions": data.impressions,
            "clicks": data.clicks,
            "units_sold": data.units_sold,
            "orders": data.orders,
            "targetting": data.targeting,
            "campaign_name": data.campaign_name,
            "asins": campaign_to_asins.get(data.campaign_id, []),
            "keyword_id": data.keyword_id,
            "keyword_type": data.keyword_type,
            "keyword_bid": data.keyword_bid,
            "search_term_date": data.search_term_date,
            "match_type": data.match_type,
            "acos": data.acos,
            "roas": data.roas,
            "cvr": data.cvr,
        })
    return result
