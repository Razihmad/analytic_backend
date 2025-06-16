# Standard Package
import logging
from datetime import timedelta

# Third party
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

# local
import utils.datetime as dt
from amazon.tasks import fetch_sales_report_by_date_range
from base.decorators import handle_exception
from amazon.services import (
    get_amazon_accounts_profile,
    get_asin_categorization_by_sales,
    get_available_regions,
    get_data_for_graph,
    get_sales_report_data,
    get_seller_asins,
    start_fetching_seller_central_data
)
from base.response import status_200, status_400


logger = logging.getLogger(__name__)


class TryApi(APIView):

    def post(self, request):
        from amazon_ads.tasks import download_file_and_process_report_data
        download_file_and_process_report_data(
            user_id=8,
            report_id='59ae20f7-78c8-45c9-b4da-51043c59c558',
            url="https://offline-report-storage-eu-west-1-prod.s3.eu-west-1.amazonaws.com/92657c52-4c63-4997-a0ba-4906051d2fad-1749665665766/report-92657c52-4c63-4997-a0ba-4906051d2fad-1749665665766.json.gz?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEAIaCWV1LXdlc3QtMSJHMEUCIBZpC27xIoS%2FnNXlo7GrpsRUrB%2BJzFU317GdE5DjXjqIAiEAyU95lTGQ09QAisUGEihWPfX3R492%2FCildRsoJYxKIA0q6gUI2%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARACGgwxMjgxMTczMzA1MTQiDLEhHWEaHgk36kDaKiq%2BBWKl143Al7YO%2BVgRgoPKZIYCG5wyqWn%2BLZZ84GR4HOmw7F%2BWbY61QkhuUnbGJymrBvO0guebjx2DFzGxvBfOBDGj1nbbj1fRIEUMejeN0WOPkpkBLkpBwCwlYD6SDeqYumwLIIxhG0cRrY1yK1XgriNbiwbLz72vsHCetxSTavae12XQmqToXQvW77gVDXi35a2mKpyA31Cn9kR5R0kk6XcXfFDeXnZGReFY%2Fw6JjZIt1bs7Ft50B17pt4p3k28QRqJmc0uy0rS5ZiK3uQuprEnN3OtnsdbUhoDXzkS91fBlw12qjPFWD%2BG%2BsK6xaiEtZJm4rdBOOduEkIjPq1gbWLCr%2BhgbnILvCJs7p2C6M6FUZTmxiZFFrEVp2guUsbMVkQrq4M7H9w9MCXDVp6DR2ivGtFWeOg9iFcE7sqvaYWcs%2BnERFqnP13yVnL1BEus%2BQQId9lQ788sVYP6VDsg8qZoLUxb05f1FpN6U5VMIIOau3JzKkXToW0srGuD40t%2FBTuWtYnpVMnyDZYfn%2BtTH3ATgVzOBRJcZC%2FxQTC%2FqLyfatMCVJy%2B520UaMb5zD1Jf9tyUGlSpPz2M2yrGQ7SHjSU68NwTsJf07uerBojggxO9jqS8%2Bf%2FAl%2BDEg6dJLqWZGZZwDtnH%2BKRY21t5ZM9%2F5Tbv%2FeE%2FWWfQUfuGJWVvGPUYCxxIJEzbGJoDuuleEQ4RykacaVoYP9v5SexUUphanxdAGQfISXnRy8NzG%2BFAqXSvAvC9HmTqbJNSR2WQToRtcYIr94l4B3NIGVcuVBHZ36xn03tzwUsIxd7mPvJmhLRAAbxkcZrlzNHuO6ia9a1pP%2FBgU8gH1PRaPsaehwexKvfuUgxXzoXVfpWCbJ9fKb37vmHD1mQmi0x3ma5NmnC7T21yCR2FJ63ewhrcP5x8NtSUKQH6QSeY6PeK8SBWLjDQiafCBjqpAS8WsV2fZUi3v%2BSLunA0DRrd0HBzfaO2B%2FWapbeEjKlvg7wD%2BMJ5bd0FAp8qYHx8H%2BmvGCjcdrygH6IdMAbp6%2Bq9h%2FuGCubNUq6tGiOK0n46fZnVYEJma58JFoZ%2FSChDKAoIlHj4icCG9lxVnVLJZJaH7gVMpC8HCMk9ydh%2B9TuXPa0bEbCpZMp%2BQFxD1s9HJehIMWlZzZdjEZ6m%2FPDKrv8Vyl7UZdsxkec%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20250611T182419Z&X-Amz-SignedHeaders=host&X-Amz-Expires=3600&X-Amz-Credential=ASIAR3VDDKJJDE2BFOMF%2F20250611%2Feu-west-1%2Fs3%2Faws4_request&X-Amz-Signature=436aeee37f291cf01cbd7b96cca83e12ccbcc6de9daa2a40d5d8263f13bf28d2",
            ad_account_id=5,
            report_type="spCampaigns",
            campaign_type="SPONSORED_PRODUCTS"
        )
        # from amazon.services import get_data_for_graph
        # get_data_for_graph(user_id=5, amazon_seller_id='A26GG6KRQ84D7L', start_date='2025-04-05', end_date='2025-04-12', asins=None, graph_data_type='TRAFFIC', prev_end_date="2025-04-12", prev_start_date="2025-04-05")
        from amazon.tasks import testing_tasks
        testing_tasks.apply_async(queue="process_report")
        return status_200(message="Hello World", data={"name": "Razi"})


class FetchSellerCentralDataAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @handle_exception
    def get(self, request):
        user_id = request.user.id
        amazon_seller_id = request.GET.get("amazon_seller_id")
        start_fetching_seller_central_data(user_id=user_id, amazon_seller_id=amazon_seller_id)
        return status_200(message="We are preparing your data for visualization")


class SalesAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @handle_exception
    def post(self, request):
        user_id = request.user.id
        logger.info(request.data)
        amazon_seller_id = request.data.get("amazon_seller_id")
        start_date = request.data.get("start_date", str(dt.now(with_tz=True).date() - timedelta(days=8)))
        end_date = request.data.get("end_date", str(dt.now(with_tz=True).date() - timedelta(days=1)))
        prev_start_date = request.data.get("prev_start_date", str(dt.now(with_tz=True).date() - timedelta(days=16)))
        prev_end_date = request.data.get("prev_end_date", str(dt.now(with_tz=True).date() - timedelta(days=9)))
        asins = request.data.get("asins")
        report = get_sales_report_data(
            user_id=user_id,
            amazon_seller_id=amazon_seller_id,
            start_date_str=start_date,
            end_date_str=end_date,
            asins=asins,
            prev_start_date=prev_start_date,
            prev_end_date=prev_end_date,
        )
        return status_200(message="Sales Data", data={"report": report})


class GetRegionsAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @handle_exception
    def post(self, request):
        regions = get_available_regions()
        return status_200(message="Regions", data={"regions": regions})


class FetchSalesReportByDate(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @handle_exception
    def post(self, request):
        user_id = request.user.id
        amazon_seller_id = request.data.get("amazon_seller_id")
        start_date = request.data.get("start_date")
        end_date = request.data.get("end_date")
        logger.info(f"{user_id=}, {amazon_seller_id=}, {start_date=}, {end_date=}")
        if not start_date or not end_date or start_date > end_date:
            return status_400(message="start data should be lesser than end date")
        fetch_sales_report_by_date_range.apply_async(args=[user_id, amazon_seller_id, start_date, end_date], queue="process_report")
        return status_200(message="Sales Data", data={})


class GetAmazonProfileData(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @handle_exception
    def post(self, request):
        user = request.user
        accounts_profile = get_amazon_accounts_profile(user_id=user.id)
        return status_200(message="Profiles", data={"accounts": accounts_profile})


class FetchSellerAsin(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @handle_exception
    def post(self, request):
        user = request.user
        amazon_seller_id = request.data.get("amazon_seller_id")
        asins = get_seller_asins(user_id=user.id, amazon_seller_id=amazon_seller_id)
        return status_200(message="Fetching Asin", data={"asins": asins})


class GetAsinTierSale(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @handle_exception
    def post(self, request):
        user = request.user
        amazon_seller_id = request.data.get("amazon_seller_id")
        start_date = request.data.get("start_date")
        end_date = request.data.get("end_date")
        tier_1, tier_2, tier_3 = get_asin_categorization_by_sales(
            user_id=user.id,
            amazon_seller_id=amazon_seller_id,
            start_date=start_date,
            end_date=end_date,
        )
        return status_200(message="Tier wise sales", data={"tier_one": tier_1, "tier_two": tier_2, "tier_three": tier_3})


class GetGraphData(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @handle_exception
    def post(self, request):
        data_type = request.data.get("graph_data_type")
        amazon_seller_id = request.data.get("amazon_seller_id")
        start_date = request.data.get("start_date", str(dt.now(with_tz=True).date() - timedelta(days=8)))
        end_date = request.data.get("end_date", str(dt.now(with_tz=True).date() - timedelta(days=1)))
        prev_start_date = request.data.get("prev_start_date", str(dt.now(with_tz=True).date() - timedelta(days=16)))
        prev_end_date = request.data.get("prev_end_date", str(dt.now(with_tz=True).date() - timedelta(days=9)))
        asins = request.data.get("asins")
        user = request.user
        logger.info(f"{request.data=}")
        current_data, prev_data = get_data_for_graph(
            user_id=user.id,
            start_date=start_date,
            end_date=end_date,
            prev_start_date=prev_start_date,
            prev_end_date=prev_end_date,
            amazon_seller_id=amazon_seller_id,
            graph_data_type=data_type,
            asins=asins
        )
        return status_200(message="graph data is here", data={"current": current_data, "previous": prev_data})
