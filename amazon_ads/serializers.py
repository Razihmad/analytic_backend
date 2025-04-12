

from collections import defaultdict
from typing import Dict, List
import pandas as pd
from django.db.models import QuerySet
from amazon_ads.constants import AdProduct
from amazon_ads.models import AmazonAdsSaleAsin


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
    data = data.groupby(["advertisedAsin", "date"], as_index=False).agg(
        {
            "sales7d": 'sum', "impressions": "sum", "clicks": "sum", "cost": "sum",
            "costPerClick": "sum", "purchases7d": "sum", "unitsSoldClicks7d": "sum"
        }
    )
    data.fillna(0)
    data = data.round(2)
    return data.to_dict(orient="records")


def group_by_sd_ad_sales_by_asin(sales: List[Dict]) -> List[Dict]:
    data = pd.DataFrame(sales)
    data = data.rename(
        columns={"sales": "sales7d", "purchases": "purchases7d", "unitsSoldClicks": "unitsSoldClicks7d", "promotedAsin": "advertisedAsin"}
    )
    data = data.groupby(["advertisedAsin", "date"], as_index=False).agg(
        {
            "sales7d": 'sum', "impressions": "sum", "clicks": "sum", "cost": "sum",
            "cost": "sum", "purchases7d": "sum", "unitsSoldClicks7d": "sum",
        }
    )
    data.fillna(0)
    data = data.round(2)
    return data.to_dict(orient="records")


def group_ad_sales_by_campaign(*, sales: List[Dict], campaign_type: str) -> List[Dict]:
    if campaign_type == AdProduct.SPONSORED_DISPLAY.value:
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
