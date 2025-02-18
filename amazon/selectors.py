from typing import List
from amazon.models import Seller, SellerCentralSale, SellerCentralTraffic, SellerCentralReturn


def get_seller_by_user_id(*, user_id: int, amazon_seller_id: str) -> Seller:
    return Seller.objects.filter(user_id=user_id, amazon_seller_id=amazon_seller_id).first()


def bulk_create_seller_central_sales(*, data: List[SellerCentralSale]):
    return SellerCentralSale.objects.bulk_create(data, ignore_conflicts=True)


def bulk_create_seller_central_traffic(*, data: List[SellerCentralTraffic]):
    return SellerCentralTraffic.objects.bulk_create(data, ignore_conflicts=True)


def bulk_create_return_data(*, data: List[SellerCentralReturn]):
    return SellerCentralReturn.objects.bulk_create(data, ignore_conflicts=True)
