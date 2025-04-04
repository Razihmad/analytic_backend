from typing import Dict, List
from amazon.models import Seller


def serialized_ads_profile_data(*, profiles: List[Dict], user_id: int, refresh_token: str, country_code: str):
    seraizlized_profiles = []
    for profile in profiles:
        if profile["countryCode"] != country_code:
            continue

        seraizlized_profiles.append({
            "country_code": profile["countryCode"],
            "currency_code": profile["currencyCode"],
            "marketplace_id": profile["accountInfo"]["marketplaceStringId"],
            "refresh_token": refresh_token,
            "amazon_seller_id": profile["accountInfo"]["id"],
            "profile_id": profile["profileId"],
            "store_name": profile["accountInfo"]["name"],
            "user_id": user_id,
        })
    return seraizlized_profiles


def serialize_seller(*, seller: Seller) -> Dict:
    return {
        "id": seller.id,
        "user_id": seller.user_id,
        "marketplace_id": seller.marketplace_id,
        "store_name": seller.store_name,
        "amazon_seller_id": seller.amazon_seller_id,
    }
