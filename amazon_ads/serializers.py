

from collections import defaultdict
from typing import Dict, List
import pandas as pd
from django.db.models import QuerySet
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


def group_ad_sales_by_asin(*, sales: List[Dict]) -> List[Dict]:
    data = pd.DataFrame(sales)
    data = data
    data = data.groupby("advertisedAsin", as_index=False).agg(
        {
            "sales7d": 'sum', "impressions": "sum", "clicks": "sum", "cost": "sum",
            "costPerClick": "sum", "spend": "sum", "purchases7d": "sum",
            "costPerClick": "sum", "data": "first", "unitsSoldClicks7d": "sum"
        }
    )
    data.fillna(0)
    return data
