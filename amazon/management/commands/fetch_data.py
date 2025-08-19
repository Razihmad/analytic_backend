from django.core.management.base import BaseCommand

from amazon.tasks import fetch_sales_report_by_date_range
from amazon_ads.tasks import start_fetching_amazon_ads_by_date_range, start_fetching_amazon_ads_campaign_by_date_range, start_fetching_search_term_report, start_fetching_targeting_report
import utils.datetime as dt
from amazon.models import Seller


class Command(BaseCommand):
    help = "Fetch data from Amazon"

    def handle(self, *args, **options):
        start_date = dt.now(with_tz=True).date() - dt.timedelta(days=8)
        end_date = dt.now(with_tz=True).date() - dt.timedelta(days=1)
        seller = Seller.objects.get(id=26)
        amazon_seller_id = seller.amazon_seller_id
        country_code = seller.country_code
        user_id = seller.user_id
        profile_id = seller.profile_id

        fetch_sales_report_by_date_range.apply_async(
            args=[seller.user_id, seller.amazon_seller_id, str(start_date), str(end_date)], queue="process_report",
        )

        start_fetching_amazon_ads_by_date_range.apply_async(
            args=[
                amazon_seller_id,
                str(start_date),
                str(end_date),
                country_code,
                profile_id,
                seller.id,
                user_id,
            ],
            queue="process_ads_report"
        )
        start_fetching_amazon_ads_campaign_by_date_range.apply_async(
            args=[
                amazon_seller_id,
                str(start_date),
                str(end_date),
                country_code,
                profile_id,
                seller.id,
                user_id,
            ],
            queue="process_ads_report"
        )
        start_fetching_search_term_report.apply_async(
            args=[
                amazon_seller_id,
                str(start_date),
                str(end_date),
                country_code,
                profile_id,
                seller.id,
                user_id,
            ],
            queue="process_ads_report"
        )
        start_fetching_targeting_report.apply_async(
            args=[
                amazon_seller_id,
                str(start_date),
                str(end_date),
                country_code,
                seller.profile_id,
                seller.id,
                user_id,
            ],
            queue="process_ads_report"
        )
