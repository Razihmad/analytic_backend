

from collections import defaultdict
from typing import Dict, List
import pandas as pd
from django.db.models import QuerySet
from amazon_ads.constants import AdProduct
from amazon_ads.models import AmazonAdsSaleAsin, AmazonAdsSaleCampaign, SearchTerm, Targeting


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
                "campaign_name": sale.campaign_name,
                "campaign_id": sale.campaign_id,
                "ad_group_name": sale.ad_group_name,
                "ad_group_id": sale.ad_group_id,
            }
        )
    return serialized_data


def group_ad_sales_by_asin(*, sales: List[Dict], campaign_type: str) -> List[Dict]:
    return prepare_data_for_insertion(sales=sales, campaign_type=campaign_type)


def prepare_data_for_insertion(*, sales: List[Dict], campaign_type: str) -> List[Dict]:
    # Prepare data for AmazonAdsSaleAsin model
    amazon_ads_sale_asin_data = []

    for item in sales:
        # Aggregate data for each ASIN on the same date
        total_sales = float(str(item.get('sales14d', 0))) if campaign_type == AdProduct.SPONSORED_PRODUCTS.value else float(str(item.get('sales', 0)))
        total_units_sold = item.get('unitsSoldClicks14d', 0) if campaign_type == AdProduct.SPONSORED_PRODUCTS.value else item.get('unitsSoldClicks', 0)
        total_cost = float(str(item.get('cost', 0)))
        total_impressions = item.get('impressions', 0)
        total_clicks = item.get('clicks', 0)
        total_orders = item.get('purchases14d', 0) if campaign_type == AdProduct.SPONSORED_PRODUCTS.value else item.get('purchases', 0)
        date = item.get('date', '')
        asin = item.get('advertisedAsin', '') if campaign_type == AdProduct.SPONSORED_PRODUCTS.value else item.get('promotedAsin', '')
        # Calculate CPC
        cpc = float('0')
        if total_clicks > 0:
            cpc = total_cost / total_clicks
        # Create model data
        model_data = {
            'asin': asin,
            'sales_date': date,
            'sales': total_sales,
            'units_sold': total_units_sold,
            'cost': total_cost,
            'impressions': total_impressions,
            'clicks': total_clicks,
            'spend': total_cost,  # spend is same as cost in this case
            'cpc': cpc,
            'orders': total_orders,
            'campaign_type': 'sponsored_products',  # Based on the data source
            'campaign_name': item.get('campaignName'),  # Taking first item's campaign name
            'campaign_id': item.get('campaignId')  # Taking first item's campaign ID
        }
        amazon_ads_sale_asin_data.append(model_data)
    return amazon_ads_sale_asin_data


def group_by_sd_ad_sales_by_asin(sales: List[Dict]) -> List[Dict]:
    data = pd.DataFrame(sales)
    data = data.rename(
        columns={
            "purchases": "orders", "unitsSoldClicks": "units_sold",
            "promotedAsin": "asin", "campaignName": "campaign_name",
            "campaignId": "campaign_id", "date": "sales_date"
        }
    )
    data.fillna(0)
    data = data.round(2)
    return data.to_dict(orient="records")


def group_ad_sales_by_campaign(*, sales: List[Dict], campaign_type: str) -> List[Dict]:
    return prepare_data_for_campaign_insertion(sales=sales, campaign_type=campaign_type)


def prepare_data_for_campaign_insertion(*, sales: List[Dict], campaign_type: str) -> List[Dict]:
    amazon_ads_sale_campaign_data = []
    for item in sales:
        total_sales = float(str(item.get('sales14d', 0))) if campaign_type == AdProduct.SPONSORED_PRODUCTS.value else float(str(item.get('sales', 0)))
        total_cost = float(str(item.get('cost', 0)))
        total_impressions = item.get('impressions', 0)
        total_clicks = item.get('clicks', 0)
        total_orders = item.get('purchases14d', 0) if campaign_type == AdProduct.SPONSORED_PRODUCTS.value else item.get('purchases', 0)
        date = item.get('date')
        cpc = float('0')
        if total_clicks > 0:
            cpc = total_cost / total_clicks

        model_data = {
            'sales_date': date,
            'sales': total_sales,
            'impressions': total_impressions,
            'clicks': total_clicks,
            'spend': total_cost,  # spend is same as cost in this case
            'cpc': cpc,
            'orders': total_orders,
            'campaign_type': campaign_type,  # Based on the data source
            'campaign_name': item.get('campaignName'),  # Taking first item's campaign name
            "campaign_status": item.get('campaignStatus'),
            "campaign_bidding_strategy": item.get('campaignBiddingStrategy', ""),
            "campaign_id": item.get('campaignId'),
        }
        amazon_ads_sale_campaign_data.append(model_data)
    return amazon_ads_sale_campaign_data


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


def serialize_search_term_report_data(*, data: List[Dict], campaign_type: str):
    return prepare_data_for_search_term_insertion(data=data, campaign_type=campaign_type)


def prepare_data_for_search_term_insertion(*, data: List[Dict], campaign_type: str) -> List[Dict]:
    amazon_ads_sale_search_term_data = []
    for item in data:
        model_data = {
            'search_term': item.get('searchTerm'),
            'keyword': item.get('keyword') if campaign_type == AdProduct.SPONSORED_PRODUCTS.value else item.get('keywordText'),
            'ad_group_name': item.get('adGroupName'),
            "ad_group_id": item.get('adGroupId'),
            'sales': item.get('sales14d') if campaign_type == AdProduct.SPONSORED_PRODUCTS.value else item.get('sales'),
            'cost': item.get('cost'),
            'impressions': item.get('impressions'),
            'clicks': item.get('clicks'),
            'units_sold': item.get('unitsSoldClicks14d') if campaign_type == AdProduct.SPONSORED_PRODUCTS.value else item.get('unitsSold'),
            'orders': item.get('purchases14d') if campaign_type == AdProduct.SPONSORED_PRODUCTS.value else item.get('purchases'),
            'targeting': item.get('targeting'),
            'campaign_name': item.get('campaignName'),
            'campaign_id': item.get('campaignId'),
            'keyword_id': item.get('keywordId'),
            'keyword_type': item.get('keywordType'),
            'keyword_bid': item.get('keywordBid'),
            'search_term_date': item.get('date'),
            'match_type': item.get('matchType'),
        }
        amazon_ads_sale_search_term_data.append(model_data)
    return amazon_ads_sale_search_term_data


def serialize_targeting_report_data(*, data: List[Dict], campaign_type: str):
    return prepare_data_for_targeting_insertion(data=data, campaign_type=campaign_type)


def prepare_data_for_targeting_insertion(*, data: List[Dict], campaign_type: str) -> List[Dict]:
    amazon_ads_sale_targeting_data = []
    for item in data:
        model_data = {
            'keyword': item.get('keyword'),
            'ad_group_name': item.get('adGroupName'),
            "ad_group_id": item.get('adGroupId'),
            'sales': item.get('sales14d') if campaign_type == AdProduct.SPONSORED_PRODUCTS.value else item.get('sales'),
            'cost': item.get('cost'),
            'impressions': item.get('impressions'),
            'clicks': item.get('clicks'),
            'units_sold': item.get('unitsSoldClicks14d') if campaign_type == AdProduct.SPONSORED_PRODUCTS.value else item.get('unitsSold'),
            'orders': item.get('purchases14d') if campaign_type == AdProduct.SPONSORED_PRODUCTS.value else item.get('purchases'),
            'targeting': item.get('targeting') if campaign_type == AdProduct.SPONSORED_PRODUCTS.value else item.get('targetingText'),
            'campaign_name': item.get('campaignName'),
            'campaign_id': item.get('campaignId'),
            'keyword_id': item.get('keywordId'),
            'keyword_type': item.get('keyword') if campaign_type == AdProduct.SPONSORED_PRODUCTS.value else item.get('keywordText'),
            'keyword_bid': item.get('keywordBid'),
            'targeting_date': item.get('date'),
            'match_type': item.get('matchType'),
            'campaign_status': item.get('campaignStatus'),
            "keyword_status": item.get('adKeywordStatus'),
            "top_of_search_is": item.get('topOfSearchImpressionShare'),
        }
        amazon_ads_sale_targeting_data.append(model_data)
    return amazon_ads_sale_targeting_data


def serialize_search_term_report(*, search_terms: QuerySet[SearchTerm], campaign_to_asins: Dict) -> List[Dict]:
    result = []
    for data in search_terms:
        result.append({
            "search_term": data.search_term,
            "keyword": data.keyword,
            "ad_group": data.ad_group_name,
            "ad_group_id": data.ad_group_id,
            "sales": data.sales,
            "cost": data.cost,
            "impressions": data.impressions,
            "clicks": data.clicks,
            "units_sold": data.units_sold,
            "orders": data.orders,
            "targetting": data.targeting,
            "campaign_name": data.campaign_name,
            "campaign_id": data.campaign_id,
            "asins": campaign_to_asins.get(data.campaign_id, []),
            "keyword_id": data.keyword_id,
            "keyword_type": data.keyword_type,
            "keyword_bid": data.keyword_bid,
            "search_term_date": data.search_term_date,
            "match_type": data.match_type,
            "campaign_type": data.campaign_type,
            "acos": round(data.cost / data.sales * 100, 3) if data.sales else 0,
            "roas": round(data.sales / data.cost, 3) if data.cost else 0,
            "cvr": round(data.orders / data.clicks * 100, 3) if data.clicks else 0,
            "cpc": round(data.cost / data.clicks, 3) if data.clicks else 0,
        })
    return result


def serialize_targeting_report(*, targeting_data: QuerySet[Targeting], campaign_to_asins: Dict) -> List[Dict]:
    result = []
    for data in targeting_data:
        result.append({
            "targeting": data.targeting,
            "keyword": data.keyword,
            "ad_group": data.ad_group_name,
            "ad_group_id": data.ad_group_id,
            "sales": data.sales,
            "cost": data.cost,
            "impressions": data.impressions,
            "clicks": data.clicks,
            "units_sold": data.units_sold,
            "orders": data.orders,
            "targetting": data.targeting,
            "campaign_name": data.campaign_name,
            "campaign_type": data.campaign_type,
            "campaign_id": data.campaign_id,
            "asins": campaign_to_asins.get(data.campaign_id, []),
            "keyword_id": data.keyword_id,
            "keyword_type": data.keyword_type,
            "keyword_bid": data.keyword_bid,
            "targeting_date": data.targeting_date,
            "match_type": data.match_type,
            "acos": round(data.cost / data.sales * 100, 3) if data.sales else 0,
            "roas": round(data.sales / data.cost, 3) if data.cost else 0,
            "cvr": round(data.orders / data.clicks * 100, 3) if data.clicks else 0,
            "cpc": round(data.cost / data.clicks, 3) if data.clicks else 0,
        })
    return result
