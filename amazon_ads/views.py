import logging
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

import utils.datetime as dt
from amazon_ads.services import fetch_ads_data_by_date, get_and_serialize_campaign_report_data, get_and_serialize_serach_term_report_data, process_campaign_sb_report_file, start_fetching_amazon_ads_data
from base.decorators import handle_exception
from base.response import status_200
# Create your views here.

logger = logging.getLogger(__name__)


class FetchAdsReport(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @handle_exception
    def post(self, request):
        amazon_seller_id = request.data.get("amazon_seller_id")
        user = request.user
        start_fetching_amazon_ads_data(amazon_seller_id=amazon_seller_id, user=user)
        return status_200(message="fetching data", data={"message": "Fetching ads report data."})


class FetchAdsReportByDate(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @handle_exception
    def post(self, request):
        amazon_seller_id = request.data.get("amazon_seller_id")
        user = request.user
        start_date = request.data.get("start_date")
        end_date = request.data.get("end_date")
        fetch_ads_data_by_date(user_id=user.id, amazon_seller_id=amazon_seller_id, start_date=start_date, end_date=end_date)
        return status_200(message="fetching data", data={"message": "Fetching ads report data."})


class UploadCampaignReportFile(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @handle_exception
    def post(self, request):
        file = request.FILES["file"]
        sales_date = request.data.get("sales_date", str(dt.now(with_tz=True).date()))
        amazon_seller_id = request.data.get("amazon_seller_id")
        process_campaign_sb_report_file(file=file, amazon_seller_id=amazon_seller_id, sales_date=sales_date, user_id=request.user.id)
        return status_200(message="Data Upserted successfully")


class GetCampaignReport(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @handle_exception
    def post(self, request):
        start_date = request.data.get("start_date", str(dt.now(with_tz=True).date() - timedelta(days=8)))
        end_date = request.data.get("end_date", str(dt.now(with_tz=True).date() - timedelta(days=2)))
        amazon_seller_id = request.data.get("amazon_seller_id")
        data, cumulative_data = get_and_serialize_campaign_report_data(
            user_id=request.user.id,
            amazon_seller_id=amazon_seller_id,
            start_date=start_date,
            end_date=end_date,
        )
        return status_200(message="campaign report fetched", data={"data": data, **cumulative_data})


class GetSearchTermReportData(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @handle_exception
    def post(self, request):
        start_date = request.data.get("start_date", str(dt.now(with_tz=True).date() - timedelta(days=8)))
        end_date = request.data.get("end_date", str(dt.now(with_tz=True).date() - timedelta(days=2)))
        amazon_seller_id = request.data.get("amazon_seller_id")
        data = get_and_serialize_serach_term_report_data(
            amazon_seller_id=amazon_seller_id,
            start_date=start_date,
            end_date=end_date,
            user_id=request.user.id,
        )
        return status_200(message="search term report fetched", data={"data": data})


class TestAccount(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]

    @handle_exception
    def get(self, request):
        logger.info(request.data)
        return status_200(message="test account", data={"message": "Test account", "data": request.data})
