from typing import Dict, Tuple
from django.contrib.auth.models import User


def get_or_create_user(*, email: str, extra_data: Dict) -> Tuple[User, bool]:
    return User.objects.get_or_create(email=email, defaults=extra_data)
