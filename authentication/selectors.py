from typing import Dict, List, Tuple
from django.contrib.auth.models import User

from amazon.models import Seller
from amazon_ads.models import AmazonAdsAccount


def get_or_create_user(*, email: str, extra_data: Dict) -> Tuple[User, bool]:
    return User.objects.get_or_create(email=email, username=email, defaults=extra_data)


def get_or_create_seller(*, partner_id: str, refresh_token: str, marketplace_id: str, user: User):
    seller, _ = Seller.objects.get_or_create(
        user=user,
        marketplace_id=marketplace_id,
        defaults={
            "refresh_token": refresh_token,
            "amazon_seller_id": partner_id,
        }
    )
    return seller


def bulk_create_profiles(*, data: List[AmazonAdsAccount]) -> List[AmazonAdsAccount]:
    return AmazonAdsAccount.objects.bulk_create(data, ignore_conflicts=True)
