from typing import Dict, List, Tuple
from django.contrib.auth.models import User

from amazon.models import Seller


def get_or_create_user(*, email: str, extra_data: Dict) -> Tuple[User, bool]:
    return User.objects.get_or_create(email=email, username=email, defaults=extra_data)


def get_or_create_seller(*, partner_id: str, refresh_token: str, marketplace_id: str, user: User):
    seller, _ = Seller.objects.update_or_create(
        user=user,
        marketplace_id=marketplace_id,
        amazon_seller_id=partner_id,
        defaults={
            "refresh_token": refresh_token,
            "amazon_seller_id": partner_id,
        }
    )
    return seller


def bulk_create_profiles(*, data: List[Seller], update_fields: List[str]) -> List[Seller]:
    return Seller.objects.bulk_create(
        data, update_conflicts=True, update_fields=update_fields, unique_fields=["user", "marketplace_id", "amazon_seller_id"]
    )
