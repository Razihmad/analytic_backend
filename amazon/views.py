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
            report_id='8f795b04-0fb9-452d-be91-5705722c0a3f',
            url="https://offline-report-storage-eu-west-1-prod.s3.eu-west-1.amazonaws.com/28de0781-e10a-4bc3-94de-6338028ffc26-1744439347190/report-28de0781-e10a-4bc3-94de-6338028ffc26-1744439347190.json.gz?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEFYaCWV1LXdlc3QtMSJIMEYCIQCwjpAL5ZmVAzZNXLpm8zrW6AxII5M47swHffi%2BN0drAAIhAJWJFkuEqSoVf1yUltrFblGVN%2FtJDYEzgQ31J6gb7XoJKuoFCM%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEQAhoMMTI4MTE3MzMwNTE0IgwhPVmRRnjpg64Y1h0qvgWYTYACmutRSJGWpl7%2FYMu7oQYK%2FIU5muJL5NvUO0ZDJJwul9Yky4luYc04nsyCA0keBKUF0nTpDxiWVXit5WmfqHRFDbeEN5JbLPJzh%2FO%2F0ATuGArCdRut4rOJImSCZaaF%2FMy4TGPtQw5wwOlGXjxQsafriuqbMPEHUrFxN9276UJ7YcOyfOj1PVmJAyTOMwAVBAVUJeOcY15Zjfr4ksHShyJSmERCxK145iYszV3J8CrnA8yFa6NNWPxiD%2FNjn6diM7GoQUSLfww33Rphha5x2inmIprXHej20gvycgeGQv43wep9bn7Q8kU19x9dVXrnYQjOxxvmEw25hPaopz%2B%2Bb03GGXMBgNACmpyfitx7q0PYixegadFyRJY6e5gU%2FT88CzgTtWyXf3KwtAvWVdMmihZDOSSeIIC3Tza%2BGqROHUhxCSX84PL5Ybh35m91w3G6HsiTZO%2B%2BDLpnB64YfMQCtYSHIvipuSXInEs1R1k%2F7DO1Y%2FApX7vYq1kBlvROrsOZMp3Xwu2DDU1TfcgoBJXvEVeoMarSqZwRxMpGNcSo1ANsxYDj3dqxzJahY8l%2FoBa7GzI%2FHFDd8%2FoxVsl1rE8kgQzHjitwMD5A0x5k3g0eZA%2F8dAnKKn889cueg7nFx9vr3H7648%2Bk31UL%2Fjd%2FET5g0Y07KWJnY3mU0771AU6OD0At6%2Bl2nk%2BmzbZBynXKD97s133ilozJpUvlqj8WdkniF1qvlKwcshQh6UQYWgEMMg73uzjOMYTbhzEu4omy76T4eOzz%2BPb7t8lUe8xFq4e1XoPp2XBMrsWNdrdsdVZYuCMZiUdCOk4IcSVThUK0X4qprIMjinlBJJU064Yzo59RcZRtOnzC0sZyE2xVZ70OWauXl4VZ9dNtK92Jsg7UYsCtGAewxBoI5taZ6Qey748MdPCdFN%2BiF4Q8W%2FCjO9ww5oXovwY6qAFVWaJHX%2BgMP10kby0U%2F4mAYlni5fDcZVxJXLU1kHU2thXFN1uCydBxgt8yOm4%2F1SWgcJd84SF%2BABgS8sxjpHsVnvNkghEyUqrDkZsZb5kWE2vwH3IQZFAH9FsDl5Tz16jv%2BuddqVHxR8xrxmtnjVooivQBxv5YNoq5zyYfdIr%2F0R2eJtiENi%2F3RLVXTCnJ9AGaMa4Dq955BY5YvgpAyGYysmSzUljnIwY%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20250412T063358Z&X-Amz-SignedHeaders=host&X-Amz-Expires=3600&X-Amz-Credential=ASIAR3VDDKJJPQQ5ULLS%2F20250412%2Feu-west-1%2Fs3%2Faws4_request&X-Amz-Signature=0ae79c6cf7a1e6dc357747cc9f76625ed9de0230b44fe5be2dce055d391cb0ea",
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
