from typing import Dict, Tuple
from django.contrib.auth.models import User

from amazon.models import Seller


def get_or_create_user(*, email: str, extra_data: Dict) -> Tuple[User, bool]:
    return User.objects.get_or_create(email=email, username=email, defaults=extra_data)


def get_or_create_seller(*, partner_id: str, refresh_token: str, access_token: str, marketplace_id: str, user: User):
    seller, _ = Seller.objects.get_or_create(
        user=user,
        marketplace_id=marketplace_id,
        defaults={
            "refresh_token": refresh_token,
            "access_token": access_token,
            "amazon_seller_id": partner_id,
        }
    )
    return seller
