from .models import AmazonAdsAccount


def get_ads_profile_by_user_and_seller_id(*, user_id: int, amazon_seller_id: int) -> AmazonAdsAccount:
    return AmazonAdsAccount.objects.filter(user_id=user_id, amazon_seller_id=amazon_seller_id).first()
