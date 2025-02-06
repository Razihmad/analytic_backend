from datetime import timedelta
import logging

from celery import shared_task
from sp_api.base import ReportType, ReportStatus, Granularity

from amazon.services import prepare_and_bulk_create_sales_data
import utils.datetime as dt
from amazon.selectors import get_seller_by_user_id
from authentication.services import get_access_token

from utils.amazon_sp_api import amazon_sp_api


logger = logging.getLogger(__name__)


@shared_task
def testing_tasks():
    print("Testing tasks")


@shared_task
def fetch_seller_central_report_data_by_date(*, user_id: int, start_datetime: str, end_datetime: str):
    logger.info(f"Fetching Seller Central data for {user_id=}")
    seller = get_seller_by_user_id(user_id=user_id)
    access_token = get_access_token(user_id=user_id)
    report_type = ReportType.GET_SALES_AND_TRAFFIC_REPORT.value
    marketplace_id = seller.marketplace_id

    response = amazon_sp_api.create_report(
        access_token=access_token,
        marketplace=marketplace_id,
        report_type=report_type,
        data={
            "reportOptions": {"dateGranularity": Granularity.DAY.value, "asinGranularity": "SKU"},
            "dataStartTime": start_datetime,
            "dataEndTime": end_datetime,
        },
    )
    logger.info(f"Report created for {user_id=}, {response=}, {start_datetime=}, {end_datetime=}")
    report_id = response.get("reportId")
    response = amazon_sp_api.get_report_by_id(
        access_token=access_token, report_id=report_id, marketplace=marketplace_id
    )
    status = response.get("processingStatus")
    while status == ReportStatus.IN_PROGRESS.value:
        response = amazon_sp_api.get_report_by_id(
            access_token=access_token, report_id=report_id, marketplace=marketplace_id
        )
        status = response.get("processingStatus")
    if status == ReportStatus.DONE.value:
        report_document_id = response.get("reportDocumentId")
        response = amazon_sp_api.get_report_document_by_id(
            access_token=access_token, document_id=report_document_id, marketplace=marketplace_id
        )
        logger.info(f"Report document fetched for {user_id=}, {response=}")
        url = response.get("url")
        logger.info(f"Report url for {user_id=}, {url=}")
        data = amazon_sp_api.get_data_by_url(url=url)
        date = data["reportSpecification"]["dataStartTime"]
        final_data = []
        for data in data["salesAndTrafficByAsin"]:
            asin_sale = {
                "seller_id": seller.id,
                "sales_date": date,
                "parent_asin": data["parentAsin"],
                "child_asin": data["childAsin"],
                "units_ordered": data["salesByAsin"]["unitsOrdered"],
                "ordered_product_sales": data["salesByAsin"]["orderedProductSales"]["amount"],
                "items_ordered": data["salesByAsin"]["totalOrderItems"],

            }
            final_data.append(asin_sale)
        prepare_and_bulk_create_sales_data(data=final_data)
        return
    logger.error(f"Report failed for {user_id=}, {response=}, {status=}, {start_datetime=}, {end_datetime=}, {seller.id=}")
