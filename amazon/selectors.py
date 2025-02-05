from amazon.models import Seller


def get_seller_by_user_id(*, user_id: int) -> Seller:
    return Seller.objects.get(user_id=user_id)
