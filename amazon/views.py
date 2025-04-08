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
    get_available_regions,
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
            report_id="ceb86cbc-8cc8-466a-bb82-d9891c8ce042",
            url="https://offline-report-storage-eu-west-1-prod.s3.eu-west-1.amazonaws.com/54e8bd25-c2fd-4b0d-99c6-01ed45fcbb17-1744140249460/report-54e8bd25-c2fd-4b0d-99c6-01ed45fcbb17-1744140249460.json.gz?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEAMaCWV1LXdlc3QtMSJGMEQCIEXIucDBIZeCQumdomIRNVNYt0CV1ly4MUESqvKeDKaEAiBmwON93%2FzPnSYS%2B4k0vTZ56vUeNeaIOGySlO6ObYlEZCrhBQh8EAIaDDEyODExNzMzMDUxNCIMfV5WIITuaIR4Dv2nKr4FX0mjVBBAWS0BlcwpQzvQCami9w6OyZFk3KCC0bz%2BqNtrpYbpbWmfKutJ7FldhKsWoAirnL88a%2FWtLYabCRVvEx0UnfjnZFdNy86mtk8LTM1sgjkOKikxkEwDFMGKIFZ4kGvbdE1cmejM2hLGgvFoOuiexmjWiLVObP%2B2UDGDAoygQnXffYHi9Vot8R7YNN3GcbWFudk5zY0K5St0KHR3ciDXifrhUhx8gjUg0zq%2FOnyRTwhjWoH8l2JTXElIp0bgKG11fJRG1DyK54muHx82yebai3h90VLCzTV5PhBfa6zFdqn6sHJSRtyDYyg1VNeb4WKT9QOQoE0xf8jZTzc4IvUBiCYo9Uk%2Bf1Qw61%2FXW8fD%2BdNewBuBGymI2L9x%2FbSVEZuX7kSq41jkssdgqM73z9Z%2FBTUJLGFDXce0O6HTvFA2I%2Bj5rOIuDpQNnSO7Lex5u3mCNiwzIsojtytvKFSZSugO7EdP0L0Q2gK%2BsO2%2FGumPCM1W0oa3WtZLisZHT7oOo%2FNFWTyjIzVBzsQvlS2SPc5v2%2B%2BFGXsP1Y%2BuLaLLX8JbngqXXQL3oI5ftqi43ZWN9JCrLLba1jkranaxOGUclxk3CmbCDkKfwu%2F%2ByuMhLvoeAkAuwuE2%2FZZpxHzUiu0Vjr3LjyDBLqe0mKY0yW%2B2PjND2%2F8tiWEm%2F09N9ko5zILr26aWGLq2DNief%2Bdt7uEfGeN2mmsA8YJlIEMQVgjgn4E14bVT6BFwc88HZeeVnaVUbiLzXeutm4TbHeBuibAt8lWX1iZA3q6yzkVnzC0I2%2F8HaUbRZmukWY4TQzwqh1F3B2HmlTCuUJGH5BkHeBnUd7P6%2B7e8o8IlQzy4LcKli3izwvoPIZFFlIyNWxu39UK4KUBGiC4TXzaOOmw7ClyLWHbdTc%2BLPQB8BHZJCfhjbTwc3uEtwuwWHAEhV%2B3IMK3m1b8GOqoB0yKq7MPQBEweYahgNc%2FRfXL%2FOh%2FDhq4IVMNwLhVZuFPlP%2FF%2FHch0kccMqZWxK4Ww8BQQiCfPGe96QdHtla8%2FhyeKnWC9%2BFb0b%2F8iundQnY53v5GM56PvS0UiBEBgn4jtCLdyHmenNUWFcCPja%2Fr8Ykw3XVzhLLO6koaTcQIhz2rsH2Mz87s5P580566dNXmD7pL2itE51zkfzcL4bJSx8W%2BII3XG225c7Hs%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20250408T192859Z&X-Amz-SignedHeaders=host&X-Amz-Expires=3600&X-Amz-Credential=ASIAR3VDDKJJGR6OY3FY%2F20250408%2Feu-west-1%2Fs3%2Faws4_request&X-Amz-Signature=1086592a10d7478b6436c33157946b1ed60ad661f0a20af6bd30f70844eefadf",
            ad_account_id=5,
            report_type="sdAdvertisedProduct",
            campaign_type="SPONSORED_DISPLAY"
        )
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
        report, performer_asins = get_sales_report_data(
            user_id=user_id,
            amazon_seller_id=amazon_seller_id,
            start_date_str=start_date,
            end_date_str=end_date,
            asins=asins,
            prev_start_date=prev_start_date,
            prev_end_date=prev_end_date,
        )
        return status_200(message="Sales Data", data={"report": report, "performer_asins": performer_asins})


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
        # fetch_sales_report_by_date_range.apply_async(args=[user_id, amazon_seller_id, start_date, end_date], queue="process_report")
        fetch_sales_report_by_date_range(user_id, amazon_seller_id, start_date, end_date)
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
