from typing import Dict, List


def serialized_ads_profile_data(*, profiles: List[Dict], user_id: int, refresh_token: str):
    seraizlized_profiles = []
    for profile in profiles:
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
