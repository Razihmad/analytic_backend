import datetime
from typing import Dict, List, Optional

from django.db.models import QuerySet, Q
from django.db.models.manager import BaseManager
from amazon.models import AsinMapper, SearchQueryMarketBasket, Seller, SellerCentralSale, SellerCentralTraffic, SellerCentralReturn, RegionDetail


def get_seller_by_user_id(*, user_id: int, amazon_seller_id: str) -> Optional[Seller]:
    return Seller.objects.filter(user_id=user_id, amazon_seller_id=amazon_seller_id).first()


def bulk_create_seller_central_sales(*, data: List[SellerCentralSale]):
    return SellerCentralSale.objects.bulk_create(data, update_conflicts=True, update_fields=[
        "sales", "orders", "units_ordered"
    ], unique_fields=['seller', 'child_asin', 'sales_date', "sku"])


def bulk_create_seller_central_traffic(*, data: List[SellerCentralTraffic]):
    return SellerCentralTraffic.objects.bulk_create(
        data,
        update_conflicts=True,
        update_fields=[
            "browser_sessions", "mobile_app_sessions", "browser_page_views",
            "mobile_app_page_views", "unit_sessions_percentage",
        ],
        unique_fields=['seller', 'child_asin', 'sessions_date', "sku"]
    )


def bulk_create_return_data(*, data: List[SellerCentralReturn]):
    return SellerCentralReturn.objects.bulk_create(data, ignore_conflicts=True)


def get_seller_central_sales_data(
    *, seller: Seller, start_date: datetime.date, end_date: datetime.date, asins: Optional[List[str]], fields: Optional[List[str]], query_params: Optional[Dict] = None
) -> QuerySet[SellerCentralSale]:
    base_filter = Q(seller=seller, sales_date__gte=start_date, sales_date__lte=end_date)
    if asins:
        base_filter &= Q(child_asin__in=asins)
    if query_params:
        for param, value in query_params.items():
            if "__" in param:
                field, lookup = param.split("__", 1)
            else:
                field, lookup = param, "exact"
            lookup_exp = f"{field}__{lookup}"
            base_filter &= Q(**{lookup_exp: value})

    data = SellerCentralSale.objects.filter(base_filter)
    if fields:
        return data.values("sales_date", *fields)
    return data


def get_seller_central_traffic_data(*, seller: Seller, start_date: datetime.date, end_date: datetime.date, asins: Optional[List[str]] = None) -> QuerySet[SellerCentralTraffic]:
    base_filter = Q(seller=seller, sessions_date__gte=start_date, sessions_date__lte=end_date)
    if asins:
        base_filter &= Q(child_asin__in=asins)
    return SellerCentralTraffic.objects.filter(base_filter)


def get_regions() -> BaseManager[RegionDetail]:
    return RegionDetail.objects.all()


def get_amazon_accounts_by_user_id(*, user_id: int) -> QuerySet[Seller]:
    return Seller.objects.filter(user_id=user_id)


def get_amazon_accounts_profile_by_user_id(*, user_id: int):
    return Seller.objects.filter(user_id=user_id)


def get_all_asins_of_seller(*, seller_id: int) -> List[int]:
    return list(SellerCentralSale.objects.filter(seller_id=seller_id).values_list("parent_asin", flat=True).distinct())


def bulk_create_search_query_market_basket(*, data: List[SearchQueryMarketBasket]):
    return SearchQueryMarketBasket.objects.bulk_create(data, ignore_conflicts=True)


def get_asin_mapper_by_asins(*, asins: List[str]) -> List[AsinMapper]:
    return AsinMapper.objects.filter(asin__in=asins)
