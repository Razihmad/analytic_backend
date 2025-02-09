import logging

from celery import shared_task
from sp_api.base import ReportType, ReportStatus, Granularity


from utils.amazon_sp_api import amazon_sp_api


logger = logging.getLogger(__name__)


@shared_task
def testing_tasks():
    print("Testing tasks")


@shared_task
def fetch_seller_central_report_data_by_date(*, user_id: int, seller_id: int, marketplace: str, start_datetime: str, end_datetime: str):
    from authentication.services import get_access_token

    logger.info(f"Fetching Seller Central data for {user_id=}")
    access_token = get_access_token(user_id=user_id)
    report_type = ReportType.GET_SALES_AND_TRAFFIC_REPORT.value

    response = amazon_sp_api.create_report(
        access_token=access_token,
        marketplace=marketplace,
        report_type=report_type,
        data={
            "reportOptions": {"dateGranularity": Granularity.DAY.value, "asinGranularity": "SKU"},
            "dataStartTime": start_datetime,
            "dataEndTime": end_datetime,
        },
    )
    logger.info(f"Report created for {user_id=}, {response=}, {start_datetime=}, {end_datetime=}")
    report_id = response.get("reportId")
    get_report_and_process_data.delay(user_id=user_id, seller_id=seller_id, report_id=report_id)


@shared_task
def get_report_and_process_data(*, user_id: int, seller_id: int, report_id: str, access_token: str, marketplace_id: str):

    response = amazon_sp_api.get_report_by_id(
        access_token=access_token, report_id=report_id, marketplace=marketplace_id
    )
    status = response.get("processingStatus")
    while status == ReportStatus.IN_PROGRESS.value:
        return get_report_and_process_data.retry(countdown=5)
    if status == ReportStatus.DONE.value:
        report_document_id = response.get("reportDocumentId")
        return process_report_document.delay(
            access_token=access_token,
            document_id=report_document_id,
            marketplace=marketplace_id,
            user_id=user_id,
            seller_id=seller_id,
        )

    logger.error(f"Report failed for {user_id=}, {response=}, {status=}, {seller_id=}")


@shared_task
def process_report_document(*, access_token: str, document_id: str, marketplace: str, user_id: int, seller_id: int):
    from amazon.services import prepare_and_bulk_create_sales_data
    response = amazon_sp_api.get_report_document_by_id(
        access_token=access_token, document_id=document_id, marketplace=marketplace
    )
    logger.info(f"Report document fetched for {user_id=}, {response=}")
    url = response.get("url")
    data = amazon_sp_api.get_data_by_url(url=url)
    date = data["reportSpecification"]["dataStartTime"]
    final_data = []
    for data in data["salesAndTrafficByAsin"]:
        asin_sale = {
            "seller_id": seller_id,
            "sales_date": date,
            "parent_asin": data["parentAsin"],
            "child_asin": data["childAsin"],
            "units_ordered": data["salesByAsin"]["unitsOrdered"],
            "ordered_product_sales": data["salesByAsin"]["orderedProductSales"]["amount"],
            "items_ordered": data["salesByAsin"]["totalOrderItems"],
        }
        final_data.append(asin_sale)
    prepare_and_bulk_create_sales_data(data=final_data)
