from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from amazon_ads.services import get_ads_sales
from base.decorators import handle_exception
import utils.datetime as dt
from amazon.services import get_total_sales, start_fetching_seller_central_data
from base.response import status_200

# Create your views here.
import logging

logger = logging.getLogger(__name__)


class TryApi(APIView):
    def get(self, request):
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
    def get(self, request):
        pass
        user_id = request.user.id
        amazon_seller_id = request.GET.get("amazon_seller_id")
        start_date = request.GET.get("start_date", dt.now(with_tz=True).date() - timedelta(days=8))
        end_date = request.GET.get("end_date", dt.now(with_tz=True).date() - timedelta(days=1))
        sales_data = get_total_sales(
            user_id=user_id, amazon_seller_id=amazon_seller_id, start_date=start_date, end_date=end_date
        )
        ads_sales = get_ads_sales(
            user_id=user_id, amazon_seller_id=amazon_seller_id, start_date=start_date, end_date=end_date
        )
        sales_data_report = 
        return status_200(message="Sales Data", data={"sales": sales_data})
