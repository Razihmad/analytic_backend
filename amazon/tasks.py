import logging
from datetime import timedelta

from celery import shared_task
from sp_api.base import ReportType, ReportStatus, Granularity

from amazon.selectors import get_seller_by_user_id
from authentication.services import get_access_token
import utils.datetime as dt
from amazon.utils.amazon_sp_api import amazon_sp_api
from utils.utils import convert_xml_to_json

logger = logging.getLogger(__name__)


@shared_task
def testing_tasks():
    logger.info("This is only for testin purpose")


@shared_task
def fetch_seller_central_report_data_by_date(
    user_id: int, seller_id: int, marketplace: str, amazon_seller_id: str
):
    logger.info(f"Fetching Seller Central data for {user_id=}")
    status = ReportStatus.IN_PROGRESS.value
    start_date = dt.now(with_tz=True).date() - timedelta(days=1)
    access_token = get_access_token(user_id=user_id, amazon_seller_id=amazon_seller_id)
    while status != ReportStatus.CANCELLED.value:
        start_date_formatting = start_date.strftime("%Y-%m-%d")
        report_type = ReportType.GET_SALES_AND_TRAFFIC_REPORT.value

        response = amazon_sp_api.create_report(
            access_token=access_token,
            marketplace=marketplace,
            report_type=report_type,
            data={
                "reportOptions": {"dateGranularity": Granularity.DAY.value, "asinGranularity": "SKU"},
                "dataStartTime": start_date_formatting,
                "dataEndTime": start_date_formatting,
            },
        )
        is_token_expire = amazon_sp_api.is_access_token_expired(response=response)
        if is_token_expire:
            access_token = get_access_token(user_id=user_id, amazon_seller_id=amazon_seller_id)
        start_date = start_date - timedelta(days=1)
        report_id = response.get("reportId")
        status = get_report_and_process_data(user_id, seller_id, report_id, access_token, marketplace, amazon_seller_id)


def get_report_and_process_data(
    user_id: int, seller_id: int, report_id: str, access_token: str, marketplace: str, amazon_seller_id: str, report_type: str
):
    logger.info(f"[get_report_and_process_data] {user_id=}, {seller_id=}, {report_id=},{marketplace=}")
    response = amazon_sp_api.get_report_by_id(
        access_token=access_token, report_id=report_id, marketplace=marketplace
    )
    is_token_expire = amazon_sp_api.is_access_token_expired(response=response)
    if is_token_expire:
        access_token = get_access_token(user_id=user_id, amazon_seller_id=amazon_seller_id)
    logger.info(f"[get_report_and_process_data] {user_id=}, {seller_id=}, {response=}, {report_id=}")
    status = response.get("processingStatus")
    if status in [ReportStatus.IN_PROGRESS.value, ReportStatus.IN_QUEUE.value]:
        return get_report_and_process_data(user_id=user_id, seller_id=seller_id, report_id=report_id, access_token=access_token, marketplace=marketplace)

    if status == ReportStatus.DONE.value:
        report_document_id = response.get("reportDocumentId")
        fetch_report_document.apply_async(
            args=[access_token, report_document_id, marketplace, user_id, seller_id, amazon_seller_id], queue="process_report"
        )

    return status


@shared_task
def fetch_report_document(
    access_token: str, document_id: str, marketplace: str, user_id: int, seller_id: int, amazon_seller_id: str,
):
    response = amazon_sp_api.get_report_document_by_id(
        access_token=access_token, document_id=document_id, marketplace=marketplace
    )
    is_token_expire = amazon_sp_api.is_access_token_expired(response=response)
    if is_token_expire:
        access_token = get_access_token(user_id=user_id, amazon_seller_id=amazon_seller_id)
        fetch_report_document.retry(countdown=1)
    logger.info(f"Report document fetched for {user_id=}, {response=}")
    url = response.get("url")
    process_report_document_and_create_entry.apply_async(args=[url, seller_id], queue="process_report")
    # process_xml_report_document_and_create_entry.apply_async(args=[url, seller_id], queue="process_report")
    # process_xml_report_document_and_create_entry(url, seller_id)


@shared_task
def process_report_document_and_create_entry(url, seller_id):
    from amazon.services import prepare_and_bulk_create_sales_data, prepare_and_bulk_create_traffic_data

    data = amazon_sp_api.get_data_by_url(url=url)
    date = data["reportSpecification"]["dataStartTime"]
    saels_data = []
    traffice_data = []
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
        asin_traffic = {
            "seller_id": seller_id,
            "sessions_date": date,
            "child_asin": data["childAsin"],
            "sku": data["sku"],
            "browser_sessions": data["trafficByAsin"]["browserSessions"],
            "mobile_app_sessions": data["trafficByAsin"]["mobileAppSessions"],
            "browser_page_views": data["trafficByAsin"]["browserPageViews"],
            "mobile_app_page_views": data["trafficByAsin"]["mobileAppPageViews"],
            "unit_sessions_percentage": data["trafficByAsin"]["unitSessionPercentage"]
        }
        traffice_data.append(asin_traffic)
        saels_data.append(asin_sale)
    prepare_and_bulk_create_sales_data(data=saels_data)
    prepare_and_bulk_create_traffic_data(data=traffice_data)
    logger.info(f"finsihed report time {dt.now(with_tz=True)=}")


@shared_task
def fetch_seller_central_return_report_data_by_date(
    user_id: int, seller_id: int, marketplace: str, amazon_seller_id: str
):
    logger.info(f"Fetching Seller Central data for {user_id=}")
    status = ReportStatus.IN_PROGRESS.value
    start_date = dt.now(with_tz=True).date() - timedelta(days=1)
    access_token = get_access_token(user_id=user_id, amazon_seller_id=amazon_seller_id)
    while status != ReportStatus.CANCELLED.value:
        data_start_time = start_date
        data_end_time = (start_date - timedelta(days=59))
        report_type = ReportType.GET_XML_RETURNS_DATA_BY_RETURN_DATE.value

        response = amazon_sp_api.create_report(
            access_token=access_token,
            marketplace=marketplace,
            report_type=report_type,
            data={
                "dataStartTime": data_start_time.strftime("%Y-%m-%d"),
                "dataEndTime": data_end_time.strftime("%Y-%m-%d"),
            },
        )
        is_token_expire = amazon_sp_api.is_access_token_expired(response=response)
        if is_token_expire:
            access_token = get_access_token(user_id=user_id, amazon_seller_id=amazon_seller_id)
        start_date = data_end_time
        report_id = response.get("reportId")
        status = get_report_and_process_data(user_id, seller_id, report_id, access_token, marketplace, amazon_seller_id)


@shared_task
def process_xml_report_document_and_create_entry(url: str, seller_id: int):
    from amazon.services import prepare_bulk_create_return_data
    xml_report = amazon_sp_api.get_xml_report_by_url(url=url)
    data = convert_xml_to_json(xml_data=xml_report)
    data = data["AmazonEnvelope"]["Message"]["return_details"]
    return_report_data = []
    for return_data in data:
        return_report = {
            "seller_id": seller_id,
            "return_request_date": return_data["return_request_date"],
            "asin": return_data["item_details"]["asin"],
            "return_delivery_date": return_data["return_delivery_date"],
            "return_type": return_data["return_type"],
            "refund_amount": return_data["refund_amount"],
            "return_quantity": int(return_data["item_details"]["return_quantity"]),
        }
        return_report_data.append(return_report)
    prepare_bulk_create_return_data(data=return_report_data)


@shared_task
def fetch_sales_report_by_date_range(user_id: int, amazon_seller_id: str, start_date: str, end_date: str):
    logger.info(f"Fetching Seller Central data for {user_id=}")
    access_token = get_access_token(user_id=user_id, amazon_seller_id=amazon_seller_id)
    logger.info(f"{access_token=}, {user_id=}, {amazon_seller_id=}, {start_date=}, {end_date=}")
    seller = get_seller_by_user_id(user_id=user_id, amazon_seller_id=amazon_seller_id)
    logger.info(f"{seller=}")
    marketplace = seller.marketplace
    start_date = dt.convert_str_to_date(date_str=start_date)
    end_date = dt.convert_str_to_date(date_str=end_date)
    logger.info(f"{access_token=}, {seller=}, {marketplace=}, {amazon_seller_id=}, {user_id=}, {start_date=}, {end_date=}")
    while start_date <= end_date:
        report_type = ReportType.GET_SALES_AND_TRAFFIC_REPORT.value
        response = amazon_sp_api.create_report(
            access_token=access_token,
            marketplace=marketplace,
            report_type=report_type,
            data={
                "reportOptions": {"dateGranularity": Granularity.DAY.value, "asinGranularity": "SKU"},
                "dataStartTime": start_date.strftime("%Y-%m-%d"),
                "dataEndTime": start_date.strftime("%Y-%m-%d"),
            },
        )
        logger.info(f"{response=}")
        is_token_expire = amazon_sp_api.is_access_token_expired(response=response)
        if is_token_expire:
            access_token = get_access_token(user_id=user_id, amazon_seller_id=amazon_seller_id)
        start_date = start_date + timedelta(days=1)
        report_id = response.get("reportId")
        logger.info(f"{user_id=}, {report_id=}, {start_date=}")
        get_report_and_process_data_task.apply_async(args=[user_id, seller.id, report_id, access_token, marketplace, amazon_seller_id], queue="process_report")


@shared_task
def get_report_and_process_data_task(
    user_id: int, seller_id: int, report_id: str, access_token: str, marketplace: str, amazon_seller_id: str
):
    logger.info(f"[get_report_and_process_data] {user_id=}, {seller_id=}, {report_id=},{marketplace=}")
    response = amazon_sp_api.get_report_by_id(
        access_token=access_token, report_id=report_id, marketplace=marketplace
    )
    is_token_expire = amazon_sp_api.is_access_token_expired(response=response)
    if is_token_expire:
        access_token = get_access_token(user_id=user_id, amazon_seller_id=amazon_seller_id)
    logger.info(f"[get_report_and_process_data] {user_id=}, {seller_id=}, {response=}, {report_id=}")
    status = response.get("processingStatus")
    if status in [ReportStatus.IN_PROGRESS.value, ReportStatus.IN_QUEUE.value]:
        return get_report_and_process_data_task.apply_async(
            args=[
                user_id, seller_id, report_id, access_token, marketplace
            ],
            countdown=20,
            queue="process_report"
        )

    if status == ReportStatus.DONE.value:
        report_document_id = response.get("reportDocumentId")
        fetch_report_document.apply_async(
            args=[access_token, report_document_id, marketplace, user_id, seller_id, amazon_seller_id], queue="process_report"
        )

    return status
