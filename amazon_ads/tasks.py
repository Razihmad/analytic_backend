from datetime import timedelta

from celery import shared_task

from amazon_ads.selectors import bulk_upsert_amazon_ads_campaign_sales, bulk_upsert_amazon_ads_sales
from amazon_ads.services import prepare_campaing_level_data_for_upsert, prepare_data_to_bulk_upsert
from authentication.services import get_ads_access_token
from utils.utils import get_region_by_country_code
import utils.datetime as dt

from amazon_ads.constants import AdProduct, AdsReportTypeId, GroupBy, ReportStatus
from amazon_ads.utils.amazon_ads_api import amazon_ads_api


@shared_task
def start_fetcing_ad_sales_data_by_asin(
    country_code: str, user_id: int, amazon_seller_id: str, profile_id: str, amazon_ad_id: int
):
    i = 0
    report_type = AdsReportTypeId.SP_ADVERTISED_PRODUCT.value
    group_by = GroupBy.ADVERTISER.value
    columns = [
        "date",
        "costPerClick",
        "clickThroughRate",
        "advertisedAsin",
        "impressions",
        "clicks",
        "cost",
        "cost",
        "spend",
        "sales1d",
        "sales7d",
        "sales14d",
        "unitsSoldClicks1d",
        "unitsSoldClicks7d",
        "unitsSoldClicks14d",
    ]
    ad_product = AdProduct.SPONSORED_PRODUCTS.value
    time_unit = "DAILY"
    current_date = dt.now(with_tz=True) - timedelta(days=1)
    region = get_region_by_country_code(country_code=country_code)
    access_token = get_ads_access_token(user_id=user_id, amazon_seller_id=amazon_seller_id, region=region)
    while i < 10:
        start_date = current_date - timedelta(days=31)
        data = amazon_ads_api.prepare_payload_for_report(
            report_type=report_type,
            name=f"{report_type} | {start_date}-{current_date}",
            start_date=str(start_date),
            end_date=str(current_date),
            group_by=[group_by],
            columns=columns,
            ad_product=ad_product,
            time_unit=time_unit
        )
        current_date = start_date - timedelta(days=1)
        response = amazon_ads_api.create_report(access_token=access_token, region=region, profile_id=profile_id, data=data)
        report_id = response.get("reportId")
        if not report_id:
            print(f"report_id not found, {response=}")
            continue
        start_tasks_to_check_report_status.apply_async(
            args=[
                user_id, amazon_seller_id, region, report_id, profile_id, amazon_ad_id, report_type
            ],
            countdown=300
        )
        i += 1


@shared_task
def start_tasks_to_check_report_status(
    user_id: int,
    amazon_seller_id: str,
    region: str,
    report_id: str,
    profile_id: str,
    ad_account_id: int,
    report_type: str,
):
    access_token = get_ads_access_token(user_id=user_id, amazon_seller_id=amazon_seller_id, region=region)
    response = amazon_ads_api.get_report_status_by_report_id(access_token=access_token, region=region, report_id=report_id, profile_id=profile_id)
    status = response.get("status")
    if not status:
        print(f"status not found, {response=}")
        return
    if status == ReportStatus.PENDING.value:
        return start_tasks_to_check_report_status.apply_async(
            args=[
                user_id, amazon_seller_id, region, report_id, profile_id, ad_account_id, report_type
            ],
            countdown=300
        )

    elif status == ReportStatus.COMPLETED.value:
        print(f"report is completed,{user_id=}, {report_id=}")
        url = response.get("url")
        download_file_and_process_report_data.apply_async(args=[user_id, report_id, url, ad_account_id, report_type])


@shared_task
def download_file_and_process_report_data(user_id: int, report_id: str, url: str, ad_account_id: int, report_type: str):
    data = amazon_ads_api.get_data_by_url(url=url)
    print(f"report data fetched, {user_id=}, {report_id=}")
    if report_type == AdsReportTypeId.SP_ADVERTISED_PRODUCT.value:
        data = prepare_data_to_bulk_upsert(data=data, user_id=user_id, ad_account_id=ad_account_id)
        bulk_upsert_amazon_ads_sales(data=data)
        return
    if report_type == AdsReportTypeId.SP_CAMPAIGN.value:
        data = prepare_campaing_level_data_for_upsert(data=data, user_id=user_id, ad_account_id=ad_account_id)
        bulk_upsert_amazon_ads_campaign_sales(data=data)
        return


@shared_task
def start_fetching_ad_sales_data_by_campaign(
    country_code: str, user_id: int, amazon_seller_id: str, profile_id: str, amazon_ad_id: int
):
    i = 0
    report_type = AdsReportTypeId.SP_CAMPAIGN.value
    group_by = GroupBy.CAMPAIGN.value
    columns = [
        "date",
        "costPerClick",
        "clickThroughRate",
        "campaignName",
        "impressions",
        "clicks",
        "cost",
        "cost",
        "spend",
        "sales1d",
        "sales7d",
        "sales14d",
        "unitsSoldClicks1d",
        "unitsSoldClicks7d",
        "unitsSoldClicks14d",
        "campaignBiddingStrategy",
        "campaignStatus",
        "campaignId",
    ]
    ad_product = AdProduct.SPONSORED_PRODUCTS.value
    time_unit = "DAILY"
    current_date = dt.now(with_tz=True) - timedelta(days=1)
    region = get_region_by_country_code(country_code=country_code)
    access_token = get_ads_access_token(user_id=user_id, amazon_seller_id=amazon_seller_id, region=region)
    while i < 10:
        start_date = current_date - timedelta(days=31)
        data = amazon_ads_api.prepare_payload_for_report(
            report_type=report_type,
            name=f"{report_type} | {start_date}-{current_date}",
            start_date=str(start_date),
            end_date=str(current_date),
            group_by=[group_by],
            columns=columns,
            ad_product=ad_product,
            time_unit=time_unit
        )
        current_date = start_date - timedelta(days=1)
        response = amazon_ads_api.create_report(access_token=access_token, region=region, profile_id=profile_id, data=data)
        report_id = response.get("reportId")
        if not report_id:
            print(f"report_id not found, {response=}")
            continue
        start_tasks_to_check_report_status.apply_async(args=[user_id, amazon_seller_id, region, report_id, profile_id, amazon_ad_id, report_type], countdown=300)
        i += 1
