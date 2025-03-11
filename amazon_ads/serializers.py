from typing import Dict, List
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
            }
        )
    return serialized_data
