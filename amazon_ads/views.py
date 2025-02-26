from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from amazon_ads.services import start_fetching_amazon_ads_data
from base.response import status_200
# Create your views here.


class FetchAdsReport(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        amazon_seller_id = request.GET.get("amazon_seller_id")
        user = request.user
        start_fetching_amazon_ads_data(amazon_seller_id=amazon_seller_id, user=user)
        return status_200(message="fetching data", data={"message": "Fetching ads report data."})
