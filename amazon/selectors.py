from typing import List
from amazon.models import Seller, SellerCentralSale


def get_seller_by_user_id(*, user_id: int) -> Seller:
    return Seller.objects.get(user_id=user_id)


def bulk_create_seller_central_sales(*, data: List[SellerCentralSale]):
    return SellerCentralSale.objects.bulk_create(data, ignore_conflicts=True)
