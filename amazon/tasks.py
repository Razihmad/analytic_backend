from celery import shared_task


@shared_task
def testing_tasks():
    print("Testing tasks")


@shared_task
def fetch_seller_central_data(user_id: int):
    print(f"fetching data for {user_id=}")
