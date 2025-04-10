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
            report_id='8f795b04-0fb9-452d-be91-5705722c0a3f',
            url="https://offline-report-storage-eu-west-1-prod.s3.eu-west-1.amazonaws.com/8f795b04-0fb9-452d-be91-5705722c0a3f-1744222108305/report-8f795b04-0fb9-452d-be91-5705722c0a3f-1744222108305.json.gz?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEBoaCWV1LXdlc3QtMSJIMEYCIQDFvHvwkrxZt%2FV7%2Bn1DUmp5CyB2XI3L9QeWvNn40jcjXgIhALLUmW2T1wus4osux0EvCtMiIFLVww0qUa%2FgKRg3iX29KuoFCJP%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEQAhoMMTI4MTE3MzMwNTE0IgyJlXsPq5Qwdbt26v4qvgXmbS46qYZhbRQmiXH%2Bt9xjXvWV6cLj0ZVvGqI%2FU1GEVCMO3KxjIBw39qJ2nhmf5qq03fYYSmZL0%2B9v%2FsAiIaNkFBqZsho0I8UCkbGWv3OXWo%2F017%2FNEXQ%2BCP2uNDDACl1IslgQtYDyhYoRq3AZloDPauPVx1RiWTGjdq%2B8mB2sN91jeA%2FNUZpXyH1TnJ60%2FTbObXmggJgLCoR%2BXTW%2B3qs134Oof1ZcAPE63pRcoq4U3IRGsD6o05dWaRccNNNC%2FYDBXN5oqtuupYa%2FvOwJG3wgPVuQUOqY9buOmGOo0hI0%2Betw68Lw%2BD%2FvM5IrIAq%2B3LwX0bHNN1dFGSmPiYSp67S83aJpn8IuNkL5gGa4rtQvsj5ZGX0Ar%2FTbfzW1QbPvkTUX1weRkzwygOVwSDRqiOtyAxTjWnZNAv5U4VSC2bdb4jei77mA61LABaAZ87%2FN%2FwlrkdZo4uTVFg3sAgWIWsN8VR%2BZB0%2BAkP4VoArCumXFtrfC%2BrlyFJ8DfqLJpSuldUL8RCstj55slqX7ezTY6mcc%2FDVEuhC3Z5ShhEuZMoL%2FEa0YSa11BX0RvOXUjmVY3wrDnBBuv2TugJykABgxrJyJb%2F4qDkCE9rqgL2XUTGiaRtEJ%2Bxbi6a9c1V3oTgS5QH5UW6STEj%2Brr0N582kZSFiKrIdkItCyyYDXzZvbhxnOE6i%2FBsP99iJ%2FEOHmOH2%2BiE9MyW7D%2B91hxOI3LxHPizqarmifwMUdaic4ci0S21%2B4cYBqRxhSguPsStuZ59SKor5s%2B2Qi7OIgFzkizCRN0nSiQMu8vxKNn%2FqNKCXShDiRZPzLzCde9zeO%2FdyLZuA4taK57aAW4aKLQuWs4c48dQq4pr3OD7o5FLIZ16LQom36v2SeKVsEIPBn44cKcZcmwh8F7G50iGGnkd328CFFOvu73xv0adw%2BV%2F1jePHHQF0wvt%2FavwY6qAETb0257H5iRbMFdiZ%2FDKUutfYLhYpHIX11UzlgkWAc6596YQWb0516DF5Rr9OpuMPF10gBVDXPCD5UlkGvg3GSVPJii%2BHEUdPErsvBZb4GF7vOlOJOmd9Ol9dvKGPZjpk7lyt8saMme7Qy7FKG%2F1RWlR%2BFhW7eJZRcl2B2gTCxNi5Xh9RQoRWPHT7Ob65fh%2FZGMVoOIoXTmTUKqC%2BKlbtykuyquGgsPBw%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20250409T181320Z&X-Amz-SignedHeaders=host&X-Amz-Expires=3600&X-Amz-Credential=ASIAR3VDDKJJEXFOUKTR%2F20250409%2Feu-west-1%2Fs3%2Faws4_request&X-Amz-Signature=d678c87980c5b74b50bfaa6087a71202e82b50e8c431acc5a9aedacd2ee6d534",
            ad_account_id=5,
            report_type="sdCampaigns",
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
