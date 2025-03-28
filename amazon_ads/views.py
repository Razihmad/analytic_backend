from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from amazon_ads.services import fetch_ads_data_by_date, start_fetching_amazon_ads_data, validate_incoming_data
from base.decorators import handle_exception
from base.exception import ServiceException
from base.response import status_200
# Create your views here.


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
        # validate_incoming_data(amazon_seller_id=amazon_seller_id, start_date=start_date, end_date=end_date)
        fetch_ads_data_by_date(user_id=user.id, amazon_seller_id=amazon_seller_id, start_date=start_date, end_date=end_date)
