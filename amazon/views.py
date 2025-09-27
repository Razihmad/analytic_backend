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
    get_product_analysis,
    get_sales_report_data,
    get_seller_asins,
    start_fetching_seller_central_data
)
from base.response import status_200, status_400


logger = logging.getLogger(__name__)


class TryApi(APIView):

    def post(self, request):
        from amazon_ads.tasks import download_file_and_process_report_data
        query_params = request.query_params
        logger.info(f"{query_params=}")
        # download_file_and_process_report_data(
        #     user_id=9,
        #     report_id='59ae20f7-78c8-45c9-b4da-51043c59c558',
        #     url="https://offline-report-storage-eu-west-1-prod.s3.eu-west-1.amazonaws.com/c7426520-2cc2-4ce7-a165-9de8fa609b69-1753811448295/report-c7426520-2cc2-4ce7-a165-9de8fa609b69-1753811448295.json.gz?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEIH%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCWV1LXdlc3QtMSJIMEYCIQDi08WTyn061Lj605z%2FrSRsG8GrIKmnUIQe%2FnyDt9ylbwIhAL8ELqcIxuYFjYZaGG1xQ4tnVhcnZDykeA%2Fk7xXat1zPKuoFCKr%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEQAhoMMTI4MTE3MzMwNTE0IgzGgBcOrRmBtvgPMOwqvgWAXG3HUDF1pPaaN%2FvXYYpexTv%2FJuHtWix3sQ2uibcevgl1DljgZyeY0Jk4dpfaDHMPwN5AKIx6h8Ao3UkbVTNoIls6iattTCUkF7G5wUwYwwJmRQ8mfktManLHvk5gaT8ZcLr7iFBiz4svaBDRXLOIwtkRcbukl8sZZpd%2FWoo%2FNvmt1Nde5Ydjvv9fF6Hmfkjm9Ppmn5gi%2BSm99bx1Cfb%2FsGT3bfL0W83bvWiyvt314w1GvQh7vIvvgQKNuCj6mySIJCettOX1%2Fyq7gL5IcGxCJ1uagrW5JIM8ZUFGSSk%2Ft9WLI%2FFyG5GsuwLxF8XqvH7fvg4semK%2FQjpg1GuKilNnZUV0YMKVyagfeFMWrWtoH%2B7ysEQekb4QCOSjyEDcHPWybZH87YLOgGAH2araB74vZuDv8y6XKll%2Bz0o1gHXJ5bvd1p65EGhqyqAOMFrrCniTdt3Nsvg3yZk0uMv2muVdovNPxxNVXQt%2B30uBYR2V%2FrqaGXGXcLHcuEvAuMVHuFYkhaIJ3RTCe3Wa%2BqwFp2YEaZtvh3%2B9g43T%2FT5eL35Q%2F9HmL1wOIfUkdM1TMdeVFMzNnetbstKfp2%2FLGIo9KF5IECT%2BG64tOaqRN8HTySuDwptwUKiLRyK5bgdoLp4OzVBnKD8TEeeaCfhG16QC0iwLZF2AwsoAOWyrTYHumlhROhvawrN%2FjqZ6Kot3bkcI6j7AR68WZ0fTMe8MBz9716mUYeCXJknfjHSExhVFXqs6%2FArp5eGo%2FAH052JUGxsNDxRAZLfcaZoS5uIE0I68X1aigyjQEAKcQk9IzvDTgZu85bYYfc0MN6PENPycxcV%2FnoaFdGl1w1w8za2Z%2FapuNFo7Mjj%2B0XCpaPGcchRXZRemy1EYWCfhx8CjAux1SqcEBqAAMmLJcvPLym3%2FHiOwpEA4mjkDvgR5F2%2Be3bPL7HowiP%2BjxAY6qAEzB94HeLAllBdQb6%2FXDH%2F9Fhhv4BrBDMP0xjZy6DhXTtYx00rkH%2BYlesy4q5X11l7c%2BcS%2BjSW4WAMO5Fszed2GTqdTgsveLwxYeUjgS590arOvE1Wetou5C39hJdtEOSi3smprByedlnm7WbBvNXp4BHASnC8FZAKk70aOKP%2BVwjRuZRe507I7TaUN%2B2fIm9eSwmknm%2F3CqcDLlxMQ%2BOJ8X0cFgCZh9JE%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20250729T175543Z&X-Amz-SignedHeaders=host&X-Amz-Expires=3600&X-Amz-Credential=ASIAR3VDDKJJGICHZY2T%2F20250729%2Feu-west-1%2Fs3%2Faws4_request&X-Amz-Signature=dc5f55e1b5e6dc0ad1babc5f033683efab9a35834f64c3df420f1ee187a244a7",
        #     ad_account_id=26,
        #     report_type="spTargeting",
        #     campaign_type="SPONSORED_PRODUCTS"
        # )
        from amazon_ads.utils.amazon_ads_api import amazon_ads_api
        response = amazon_ads_api.update_target_bid_by_target_id(
            access_token="Atza|IwEBIGFhOmjX8jlYEPSJ0k0ttq4q-x-U2_YHBaoIdv5qZz9E0cBWUjKoFp491fSMz7hEweMF7l_SxDcj2xF9LfTgtvL5k9-I0lUoBgquX_vaTJxEtXxWGZlwO2rQyihnr2FvAKGClDFM6L-8Yjz0ScRZBgIpEuT8m7-gRUj7lO3zFc7fYQZFjVePZSV44UjQ2dNh0luEJi0eSY0KWgsJz2A2F6IJQEqQJ696-0EAUYNBYT88Gznagp5-lwbe-aiEdKRPE_67hZacmoc1nL-VjAo_TeuTyXB9t8G3WO0cIjAC_OkKcWUxd6z2UflGVoUV1KRZ7ODf7q0FXvFsshU2RWisybyYt5ORrmQN8PrzTTb_CZbgAQnSA6_sTrDK755g1_443nt1nIhQ5oNgX5vDdkD7qPCYsyfM1uh-mq3JPfWGXnwPKb2jTmGSFqiBKw7Y17YvsOXJjeoYWwh-MrFRuywLMDVSw-gdhC1uuzs2IbiGnqVEwc9dN-yquSJ_t4ZBryIQUlMQ986ge11g0QVVoqgeNoQtex3tg7qOFmEi6e8iISk9oA",
            region="eu-west-1",
            profile_id="1406427077937190",
            endpoint="/sp/targets",
            data={'targetingClauses': [{'bid': 17.18, 'targetId': '166723612143632'}]},
            content_type="application/vnd.spTargetingClause.v3+json",
        )
        logger.info(f"{response=}")
        # # from amazon.services import get_data_for_graph
        # # get_data_for_graph(user_id=5, amazon_seller_id='A26GG6KRQ84D7L', start_date='2025-04-05', end_date='2025-04-12', asins=None, graph_data_type='TRAFFIC', prev_end_date="2025-04-12", prev_start_date="2025-04-05")
        # from amazon.tasks import testing_tasks
        # testing_tasks.apply_async(queue="process_report")
        return status_200(message="Hello World", data={"name": "Razi", "response": response})


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
        report = get_sales_report_data(
            user_id=user_id,
            amazon_seller_id=amazon_seller_id,
            start_date_str=start_date,
            end_date_str=end_date,
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
        prev_start_date = request.data.get("prev_start_date")
        prev_end_date = request.data.get("prev_end_date")
        tier_1, tier_2, tier_3 = get_asin_categorization_by_sales(
            user_id=user.id,
            amazon_seller_id=amazon_seller_id,
            start_date=start_date,
            end_date=end_date,
            prev_start_date=prev_start_date,
            prev_end_date=prev_end_date,
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


class GetProductAnalysis(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @handle_exception
    def post(self, request):
        user = request.user
        amazon_seller_id = request.data.get("amazon_seller_id")
        start_date = request.data.get("start_date")
        end_date = request.data.get("end_date")
        asins = request.data.get("asins", [])
        query_params = request.query_params

        logger.info(f"{asins=}, {start_date=}, {end_date=}, {amazon_seller_id=}, {user.id=}")
        product_analysis = get_product_analysis(
            user_id=user.id,
            amazon_seller_id=amazon_seller_id,
            start_date=start_date,
            end_date=end_date,
            asins=asins,
        )
        return status_200(message="Product Analysis", data={"product_analysis": product_analysis})
