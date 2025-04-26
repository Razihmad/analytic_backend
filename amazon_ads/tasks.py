import logging
from datetime import timedelta, date

from celery import shared_task

from amazon_ads.selectors import bulk_upsert_amazon_ads_campaign_sales, bulk_upsert_amazon_ads_sales
from amazon_ads.serializers import group_ad_sales_by_asin, group_ad_sales_by_campaign
from authentication.services import get_ads_access_token
from utils.utils import get_region_by_country_code
import utils.datetime as dt

from amazon_ads.constants import AD_PRODUCT_COLUMN_MAPPING, CAMPAIGN_COLUMNS, CAMPAIGN_TO_ADVERTISED_PRODUCT_REPORT, CAMPAIGN_TO_REPORT_TYPE_MAPPING, SP_CAMPAIGN_REPORT_COLUMNS, AdProduct, AdsReportTypeId, CampaignStatus, GroupBy, ReportStatus
from amazon_ads.utils.amazon_ads_api import amazon_ads_api

logger = logging.getLogger(__name__)


@shared_task
def start_fetcing_ad_sales_data_by_asin(
    country_code: str, user_id: int, amazon_seller_id: str, profile_id: str, amazon_ad_id: int
):
    i = 0
    current_date = dt.now(with_tz=True).date() - timedelta(days=1)
    region = get_region_by_country_code(country_code=country_code)
    access_token = get_ads_access_token(user_id=user_id, amazon_seller_id=amazon_seller_id, region=region)
    while i < 10:
        start_date = current_date - timedelta(days=31)
        create_ads_data_report_by_date(
            start_date=start_date,
            end_date=current_date,
            access_token=access_token,
            region=region,
            profile_id=profile_id,
            ad_account_id=amazon_ad_id,
            amazon_seller_id=amazon_seller_id,
            user_id=user_id,
            campaign_type=AdProduct.SPONSORED_PRODUCTS.value,
            report_type="spAdvertisedProduct"
        )
        current_date = start_date - timedelta(days=1)
        i += 1


def create_ads_data_report_by_date(
    *,
    start_date: date,
    end_date: date,
    access_token: str,
    region: str,
    profile_id: str,
    user_id: int,
    amazon_seller_id: str,
    ad_account_id: int,
    campaign_type: str,
    report_type: str,
):
    group_by = GroupBy.ADVERTISER.value
    columns = AD_PRODUCT_COLUMN_MAPPING[campaign_type]
    time_unit = "DAILY"
    logger.info(f"creating report for {start_date=}, {end_date=}, {region=}")
    data = amazon_ads_api.prepare_payload_for_report(
        report_type=report_type,
        name=f"{report_type} | {start_date}-{end_date}",
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
        group_by=[group_by],
        columns=columns,
        ad_product=campaign_type,
        time_unit=time_unit
    )
    response = amazon_ads_api.create_report(access_token=access_token, region=region, profile_id=profile_id, data=data)
    logger.info(f"report created, {response=}, {start_date=}, {end_date}")
    report_id = response.get("reportId")
    logger.info(f"report_id: {report_id=}")
    if not report_id:
        print(f"report_id not found, {response=}")
        return
    logger.info(f"report_id: {user_id=}, {amazon_seller_id=}, {region=}, {report_id=}, {profile_id=}, {ad_account_id=}, {report_type=}")
    start_tasks_to_check_report_status.apply_async(
        args=[
            user_id, amazon_seller_id, region, report_id, profile_id, ad_account_id, report_type, campaign_type,
        ],
        countdown=300,
        queue="process_ads_report"
    )


@shared_task
def start_tasks_to_check_report_status(
    user_id: int,
    amazon_seller_id: str,
    region: str,
    report_id: str,
    profile_id: str,
    ad_account_id: int,
    report_type: str,
    campaign_type: str,
):
    logger.info(f"checking report status, {report_id=}, {user_id=}, {profile_id=}")
    access_token = get_ads_access_token(user_id=user_id, amazon_seller_id=amazon_seller_id, region=region)
    response = amazon_ads_api.get_report_status_by_report_id(access_token=access_token, region=region, report_id=report_id, profile_id=profile_id)
    status = response.get("status")
    logger.info(f"report status: {status=}, {report_id=}, {campaign_type=}, {report_type=}")
    if not status:
        logger.info(f"status not found, {response=}")
        return
    if status == ReportStatus.PENDING.value:
        return start_tasks_to_check_report_status.apply_async(
            args=[
                user_id, amazon_seller_id, region, report_id, profile_id, ad_account_id, report_type, campaign_type,
            ],
            countdown=300,
            queue="process_ads_report"
        )
    elif status == ReportStatus.COMPLETED.value:
        url = response.get("url")
        logger.info(f"report is completed,{user_id=}, {report_id=}, {url=}, {ad_account_id=}")
        download_file_and_process_report_data.apply_async(args=[user_id, report_id, url, ad_account_id, report_type, campaign_type], queue="process_ads_report")


@shared_task
def download_file_and_process_report_data(user_id: int, report_id: str, url: str, ad_account_id: int, report_type: str, campaign_type: str):
    from amazon_ads.services import prepare_campaing_level_data_for_upsert, prepare_data_to_bulk_upsert

    data = amazon_ads_api.get_data_by_url(url=url)
    print(f"report data fetched, {user_id=}, {report_id=}, {len(data)=}, {url=}, {ad_account_id=}, {report_type=}, {campaign_type=}")
    if report_type in [AdsReportTypeId.SP_ADVERTISED_PRODUCT.value, AdsReportTypeId.SD_ADVERISED_PRODUCT.value]:
        data = group_ad_sales_by_asin(sales=data, campaign_type=campaign_type)
        logger.info(f"{user_id=}, {report_id=}, {ad_account_id=}, {len(data)=}")
        data = prepare_data_to_bulk_upsert(data=data, ad_account_id=ad_account_id, campaign_type=campaign_type)
        logger.info(f"{user_id=}, {report_id=}, {ad_account_id=}, {len(data)=}")
        bulk_upsert_amazon_ads_sales(data=data)
        logger.info(f"report data upserted, {user_id=}, {report_id=} {ad_account_id=}, {report_type=}")
        return
    if report_type in [AdsReportTypeId.SP_CAMPAIGN.value, AdsReportTypeId.SD_CAMPAING.value, AdsReportTypeId.SB_CAMPAIGN.value]:
        data = group_ad_sales_by_campaign(sales=data, campaign_type=campaign_type)
        logger.info(f"{user_id=}, {report_id=}, {ad_account_id=}, {len(data)=}")
        data = prepare_campaing_level_data_for_upsert(data=data, ad_account_id=ad_account_id, campaign_type=campaign_type)
        logger.info(f"{data=}")
        bulk_upsert_amazon_ads_campaign_sales(data=data)
        logger.info(f"report data upserted, {user_id=}, {report_id=} {ad_account_id=}, {report_type=}")

        return


@shared_task
def start_fetching_ad_sales_data_by_campaign(
    country_code: str, user_id: int, amazon_seller_id: str, profile_id: str, amazon_ad_id: int
):
    i = 0
    report_type = AdsReportTypeId.SP_CAMPAIGN.value
    group_by = GroupBy.CAMPAIGN.value
    columns = SP_CAMPAIGN_REPORT_COLUMNS
    status = [CampaignStatus.ENABLED.value, CampaignStatus.PAUSED.value]
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
            time_unit=time_unit,
            filters={"field": "campaignStatus", "values": status}
        )
        current_date = start_date - timedelta(days=1)
        response = amazon_ads_api.create_report(access_token=access_token, region=region, profile_id=profile_id, data=data)
        report_id = response.get("reportId")
        if not report_id:
            print(f"report_id not found, {response=}, {user_id=}, {profile_id=}")
            continue
        start_tasks_to_check_report_status.apply_async(
            args=[
                user_id, amazon_seller_id, region, report_id, profile_id, amazon_ad_id, report_type, ad_product
            ],
            countdown=300,
            queue="process_ads_report"
        )
        i += 1


@shared_task
def start_fetching_amazon_ads_by_date_range(
    amazon_seller_id: str,
    start_date: str,
    end_date: str,
    country_code: str,
    profile_id: str,
    ad_account_id: int,
    user_id: int
):
    logger.info(f"start_fetching_amazon_ads_by_date_range, {start_date=}, {end_date=}, {ad_account_id=}, {profile_id=}, {user_id=}")
    start_date = dt.convert_str_to_date(date_str=start_date)
    end_date = dt.convert_str_to_date(date_str=end_date)
    region = get_region_by_country_code(country_code=country_code)
    access_token = get_ads_access_token(user_id=user_id, amazon_seller_id=amazon_seller_id, region=region)
    for campaign_type, report_type in CAMPAIGN_TO_ADVERTISED_PRODUCT_REPORT.items():
        logger.info(f"{amazon_seller_id=}, {start_date=}, {end_date=}, {campaign_type=}, {report_type=}, {user_id=}, {profile_id=}")
        create_ads_data_report_by_date(
            start_date=start_date,
            end_date=end_date,
            access_token=access_token,
            region=region,
            profile_id=profile_id,
            user_id=user_id,
            amazon_seller_id=amazon_seller_id,
            ad_account_id=ad_account_id,
            campaign_type=campaign_type,
            report_type=report_type
        )


@shared_task
def start_fetching_amazon_ads_campaign_by_date_range(
    amazon_seller_id: str,
    start_date: str,
    end_date: str,
    country_code: str,
    profile_id: str,
    ad_account_id: int,
    user_id: int
):
    logger.info(f"start_fetching_amazon_ads_campaign_date_range, {start_date=}, {end_date=}, {ad_account_id=}, {profile_id=}, {user_id=}")
    start_date = dt.convert_str_to_date(date_str=start_date)
    end_date = dt.convert_str_to_date(date_str=end_date)
    region = get_region_by_country_code(country_code=country_code)
    access_token = get_ads_access_token(user_id=user_id, amazon_seller_id=amazon_seller_id, region=region)
    for campaign_type in AdProduct._member_names_:
        logger.info(f"[campaign type data] {amazon_seller_id=}, {start_date=}, {end_date=}, {profile_id=}, {campaign_type=}, {user_id=}")
        create_ads_campaign_data_report_by_date.apply_async(
            args=[
                start_date  ,
                end_date,
                access_token,
                region,
                profile_id,
                user_id,
                amazon_seller_id,
                ad_account_id,
                campaign_type,
            ],
            queue="process_ads_report"
        )


@shared_task
def create_ads_campaign_data_report_by_date(
    start_date: date,
    end_date: date,
    access_token: str,
    region: str,
    profile_id: str,
    user_id: int,
    amazon_seller_id: str,
    ad_account_id: int,
    campaign_type: str,
):
    report_type = CAMPAIGN_TO_REPORT_TYPE_MAPPING[campaign_type]
    group_by = GroupBy.CAMPAIGN.value
    columns = CAMPAIGN_COLUMNS[campaign_type]
    time_unit = "DAILY"

    logger.info(f"creating report for {start_date=}, {end_date=}, {region=}, {campaign_type=}")
    data = amazon_ads_api.prepare_payload_for_report(
        report_type=report_type,
        name=f"{report_type} | {start_date}-{end_date}",
        start_date=start_date.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
        group_by=[group_by],
        columns=columns,
        ad_product=campaign_type,
        time_unit=time_unit
    )
    response = amazon_ads_api.create_report(access_token=access_token, region=region, profile_id=profile_id, data=data)
    logger.info(f"report created, {response=}, {start_date=}, {end_date}")
    report_id = response.get("reportId")
    logger.info(f"report_id: {report_id=}")
    if not report_id:
        print(f"report_id not found, {response=}")
        return
    logger.info(f"report_id: {user_id=}, {amazon_seller_id=}, {region=}, {report_id=}, {profile_id=}, {ad_account_id=}, {report_type=}")
    start_tasks_to_check_report_status.apply_async(
        args=[
            user_id, amazon_seller_id, region, report_id, profile_id, ad_account_id, report_type, campaign_type,
        ],
        countdown=300,
        queue="process_ads_report"
    )
