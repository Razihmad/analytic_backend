from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from amazon.services import start_fetching_seller_central_data
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

    def get(self, request):
        user_id = request.user.id
        amazon_seller_id = request.GET.get("amazon_seller_id")
        start_fetching_seller_central_data(user_id=user_id, amazon_seller_id=amazon_seller_id)
        return status_200(message="We are preparing your data for visualization")


class SalesAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        pass
        # user_id = request.user.id
        # amazon_seller_id = request.GET.get("amazon_seller_id")
        # start_date = request.GET.get("start_date")
        # end_date = request.GET.get("end_date")
        # get_sales_data(user_id=user_id, amazon_seller_id=amazon_seller_id, start_date=start_date, end_date=end_date)
        # return status_200(message="Sales Data", data=sales_data.values())