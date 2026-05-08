import logging
from datetime import timedelta
import random

from amazon_ads.services import fetch_ads_data_by_date
from celery import shared_task
from sp_api.base import ReportType, ReportStatus, Granularity

from amazon.selectors import get_seller_by_user_id
from amazon.models import Seller
from authentication.services import get_access_token
import utils.datetime as dt
from amazon.utils.amazon_sp_api import amazon_sp_api
from utils.utils import convert_xml_to_json

logger = logging.getLogger(__name__)


@shared_task
def testing_tasks():
    logger.info("This is only for testin purpose")


@shared_task
def run_user_sales_report_for_date_minus_2(user_id: int = 2):
    from amazon_ads.services import fetch_ads_data_by_date
    from amazon.models import Seller

    target_date = (dt.now(with_tz=True).date() - timedelta(days=2)).strftime("%Y-%m-%d")
    sellers = Seller.objects.filter(user_id=user_id).values_list("amazon_seller_id", flat=True)
    logger.info(f"Queueing sales report tasks for {user_id=}, {target_date=}, sellers={len(sellers)}")
    for amazon_seller_id in sellers:
        fetch_sales_report_by_date_range.apply_async(
            args=[user_id, amazon_seller_id, target_date, target_date],
            queue="process_report",
        )
        fetch_ads_data_by_date(user_id=user_id, amazon_seller_id=amazon_seller_id, start_date=target_date, end_date=target_date)


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
        return get_report_and_process_data(user_id=user_id, seller_id=seller_id, report_id=report_id, access_token=access_token, marketplace=marketplace, report_type=report_type)

    if status == ReportStatus.DONE.value:
        report_document_id = response.get("reportDocumentId")
        fetch_report_document.apply_async(
            args=[access_token, report_document_id, marketplace, user_id, seller_id, amazon_seller_id, report_type], queue="process_report"
        )

    return status


@shared_task
def fetch_report_document(
    access_token: str, document_id: str, marketplace: str, user_id: int, seller_id: int, amazon_seller_id: str, report_type
):
    response = amazon_sp_api.get_report_document_by_id(
        access_token=access_token, document_id=document_id, marketplace=marketplace
    )
    logger.info(f"Report document fetched for {user_id=}, {response=}, {marketplace=}, {document_id=}")
    is_token_expire = amazon_sp_api.is_access_token_expired(response=response)
    if is_token_expire:
        access_token = get_access_token(user_id=user_id, amazon_seller_id=amazon_seller_id)
        fetch_report_document.retry(countdown=1)
    logger.info(f"Report document fetched for {user_id=}, {response=}")
    url = response.get("url")
    if report_type == ReportType.GET_SALES_AND_TRAFFIC_REPORT.value:
        process_report_document_and_create_entry.apply_async(args=[url, seller_id], queue="process_report", countdown=2)
        return
    if report_type == ReportType.GET_XML_RETURNS_DATA_BY_RETURN_DATE.value:
        process_xml_report_document_and_create_entry.apply_async(args=[url, seller_id], queue="process_report", countdown=2)
        return
    if report_type == ReportType.GET_BRAND_ANALYTICS_MARKET_BASKET_REPORT.value:
        process_search_query_market_basket_report_document.apply_async(args=[url, seller_id], queue="process_report", countdown=2)
        return



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
            "sales": data["salesByAsin"]["orderedProductSales"]["amount"],
            "orders": data["salesByAsin"]["totalOrderItems"],
            "sku": data["sku"],
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
        status = get_report_and_process_data(user_id, seller_id, report_id, access_token, marketplace, amazon_seller_id, report_type)


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
    prev = 0
    while start_date <= end_date:
        report_type = ReportType.GET_SALES_AND_TRAFFIC_REPORT.value
        data = {
            "reportOptions": {"dateGranularity": Granularity.DAY.value, "asinGranularity": "SKU"},
            "dataStartTime": start_date.strftime("%Y-%m-%d"),
            "dataEndTime": start_date.strftime("%Y-%m-%d"),
        }
        new_countdown = prev + random.randint(10, 100)
        logger.info(f"{new_countdown=}, ")
        create_sale_and_traffic_report.apply_async(
            args=[access_token, marketplace, report_type, data, amazon_seller_id, user_id, seller.id],
            queue="process_report"
        )
        prev = new_countdown
        start_date = start_date + timedelta(days=1)


@shared_task
def create_sale_and_traffic_report(access_token, marketplace, report_type, data, amazon_seller_id, user_id, seller_id):
    report_type = ReportType.GET_SALES_AND_TRAFFIC_REPORT.value
    response = amazon_sp_api.create_report(
        access_token=access_token,
        marketplace=marketplace,
        report_type=report_type,
        data=data,
    )
    logger.info(f"{response=}, {amazon_seller_id=}, {user_id=}, {seller_id=}")
    is_token_expire = amazon_sp_api.is_access_token_expired(response=response)
    if is_token_expire:
        access_token = get_access_token(user_id=user_id, amazon_seller_id=amazon_seller_id)
    report_id = response.get("reportId")
    logger.info(f"{user_id=}, {report_id=}")
    if not report_id:
        return
    get_report_and_process_data_task.apply_async(
        args=[user_id, seller_id, report_id, access_token, marketplace, amazon_seller_id, report_type], queue="process_report",
        countdown=20 + random.randint(0, 120)
    )


@shared_task
def get_report_and_process_data_task(
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
        return get_report_and_process_data_task.apply_async(
            args=[
                user_id, seller_id, report_id, access_token, marketplace, amazon_seller_id, report_type
            ],
            countdown=20 + random.randint(0, 100),
            queue="process_report"
        )

    if status == ReportStatus.DONE.value:
        report_document_id = response.get("reportDocumentId")
        fetch_report_document.apply_async(
            args=[access_token, report_document_id, marketplace, user_id, seller_id, amazon_seller_id, report_type],
            queue="process_report",
            countdown=20
        )

    return status


@shared_task
def fetch_search_query_market_basket_report(
    user_id: int,
    amazon_seller_id: str,
    start_date: str,
    end_date: str,
    marketplace: str,
    seller_id: int,
    report_period: str,
):
    access_token = get_access_token(user_id=user_id, amazon_seller_id=amazon_seller_id)
    start_date = dt.convert_str_to_date(date_str=start_date)
    end_date = dt.convert_str_to_date(date_str=end_date)
    logger.info(f"{access_token=}, {user_id=}, {amazon_seller_id=}, {start_date=}, {end_date=}, {marketplace=}")
    report_type = ReportType.GET_BRAND_ANALYTICS_MARKET_BASKET_REPORT.value
    response = amazon_sp_api.create_report(
            access_token=access_token,
            marketplace=marketplace,
            report_type=report_type,
            data={
                "reportOptions": {"reportPeriod": report_period},
                "dataStartTime": start_date.strftime("%Y-%m-%d"),
                "dataEndTime": end_date.strftime("%Y-%m-%d"),
            },
        )
    report_id = response.get("reportId")
    logger.info(f"{user_id=}, {report_id=}, {start_date=}")
    get_report_and_process_data_task.apply_async(
        args=[user_id, seller_id, report_id, access_token, marketplace, amazon_seller_id, report_type],
        queue="process_report",
        countdown=100 + random.randint(0, 10)
    )
    return response


@shared_task
def fetch_search_query_performance_report(user_id: int, amazon_seller_id: str, start_date: str, end_date: str, marketplace: str, seller_id: int):
    access_token = get_access_token(user_id=user_id, amazon_seller_id=amazon_seller_id)
    start_date = dt.convert_str_to_date(date_str=start_date)
    end_date = dt.convert_str_to_date(date_str=end_date)
    logger.info(f"{access_token=}, {user_id=}, {amazon_seller_id=}, {start_date=}, {end_date=}, {marketplace=}")
    report_type = ReportType.get_brand_
    # while start_date <= end_date:
    response = amazon_sp_api.create_report(
            access_token=access_token,
            marketplace=marketplace,
            report_type=report_type,
            data={
                "reportOptions": {"reportPeriod": "WEEK"},
                "dataStartTime": start_date.strftime("%Y-%m-%d"),
                "dataEndTime": end_date.strftime("%Y-%m-%d"),
            },
        )
    report_id = response.get("reportId")
    logger.info(f"{user_id=}, {report_id=}, {start_date=}")
    get_report_and_process_data_task.apply_async(
        args=[user_id, seller_id, report_id, access_token, marketplace, amazon_seller_id, report_type],
        queue="process_report",
        countdown=100 + random.randint(0, 10)
    )
    return response


def process_search_query_market_basket_report_document(url: str, seller_id: int):
    from amazon.services import prepare_and_bulk_create_search_query_market_basket_data

    data = amazon_sp_api.get_data_by_url(url=url)
    report_period = data["reportSpecification"]["reportOptions"]["reportPeriod"]
    start_date = data["reportSpecification"]["dataStartTime"]
    end_date = data["reportSpecification"]["dataEndTime"]
    data_by_asin = data["dataByAsin"]
    data_by_asin_list = []
    for data in data_by_asin:
        data_by_asin_list.append(
            {
                "seller_id": seller_id,
                "asin": data["asin"],
                "purchased_with_asin": data["purchasedWithAsin"],
                "purchased_with_rank": data["purchasedWithRank"],
                "combination_pct": data["combinationPct"],
                "report_period": report_period,
                "start_date": start_date,
                "end_date": end_date,
            }
        )
    prepare_and_bulk_create_search_query_market_basket_data(data=data_by_asin_list)


@shared_task
def test_celery_beat(user_id):
    logger.info(f"here it is working, {user_id=}")
