import datetime
from typing import List, Optional

from django.db.models import QuerySet, Q
from django.db.models.manager import BaseManager
from amazon.models import Seller, SellerCentralSale, SellerCentralTraffic, SellerCentralReturn, RegionDetail


def get_seller_by_user_id(*, user_id: int, amazon_seller_id: str) -> Optional[Seller]:
    return Seller.objects.filter(user_id=user_id, amazon_seller_id=amazon_seller_id).first()


def bulk_create_seller_central_sales(*, data: List[SellerCentralSale]):
    return SellerCentralSale.objects.bulk_create(data, ignore_conflicts=True)


def bulk_create_seller_central_traffic(*, data: List[SellerCentralTraffic]):
    return SellerCentralTraffic.objects.bulk_create(data, ignore_conflicts=True)


def bulk_create_return_data(*, data: List[SellerCentralReturn]):
    return SellerCentralReturn.objects.bulk_create(data, ignore_conflicts=True)


def get_seller_central_sales_data(
    *, seller: Seller, start_date: datetime.date, end_date: datetime.date, asins: Optional[List[str]], fields: Optional[List[str]]
) -> QuerySet[SellerCentralSale]:
    base_filter = Q(seller=seller, sales_date__gte=start_date, sales_date__lte=end_date)
    if asins:
        base_filter &= Q(child_asin__in=asins)
    data = SellerCentralSale.objects.filter(base_filter)
    if fields:
        return data.values("sales_date", *fields)
    return data


def get_seller_central_traffic_data(*, seller: Seller, start_date: datetime.date, end_date: datetime.date) -> QuerySet[SellerCentralTraffic]:
    return SellerCentralTraffic.objects.filter(seller=seller, sessions_date__gte=start_date, sessions_date__lte=end_date)


def get_regions() -> BaseManager[RegionDetail]:
    return RegionDetail.objects.all()


def get_amazon_accounts_by_user_id(*, user_id: int) -> QuerySet[Seller]:
    return Seller.objects.filter(user_id=user_id)


def get_amazon_accounts_profile_by_user_id(*, user_id: int):
    return Seller.objects.filter(user_id=user_id)


def get_all_asins_of_seller(*, seller_id: int) -> List[int]:
    return list(SellerCentralSale.objects.filter(seller_id=seller_id).values_list("parent_asin", flat=True).distinct())
