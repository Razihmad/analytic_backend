from celery import shared_task

from amazon.selectors import get_seller_by_user_id


@shared_task
def testing_tasks():
    print("Testing tasks")


@shared_task
def fetch_seller_central_data(*, user_id: int):
    seller = get_seller_by_user_id(user_id=user_id)
    access_token = seller.access_token
    refresh_token = seller.refresh_token
    
    print(f"fetching data for {user_id=}")
