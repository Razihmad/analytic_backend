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
            url="https://offline-report-storage-eu-west-1-prod.s3.eu-west-1.amazonaws.com/9bb17e8d-2be1-4008-b955-583b577f1608-1746959737085/report-9bb17e8d-2be1-4008-b955-583b577f1608-1746959737085.json.gz?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEBIaCWV1LXdlc3QtMSJHMEUCIBA7nGs7UoxMDO7CKHx4CL9ZDtZrnbTUUJrJzZ8%2FS8KMAiEA0eBtSDFqpMPvsA5myaR%2B7TxQHCEb4i57DcM%2BugU2osUq6gUIu%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FARACGgwxMjgxMTczMzA1MTQiDBaHyU4MQHzkc9tTnyq%2BBZhCI6DtxI9Dxh9AodvekTr65bB6O0aX4X5RpYowQ%2BVetyfFN1QylXU5UeSbLxAWode9hQkBU3t4d0UYL1D%2FGHUYiJVNHrn27fLr7aPl7nIXiMl16vjSg83AhuuTUb3LXGDv%2BEIlpn3iJkZG2yMXaEVozZQSCPYoz%2F9l6KRvqKDdBQbMzyq03Uq587z2BlrwldWMBKS4f%2FBpGrBfPVvaDqFx30fpdk6y7dFsBBkz2uPW9aT1OOb5R73%2FgvHD30Bd1zH53kO6SdIYqxh%2B7Zb9TjoY5wkB3QCLm%2B16cCVNQWadjIcD80MWCvWyXvONICfBHkGi9RQ9yC3HMHDWUlhAe1SNTeWeq03%2F7fuAWaC4jZXm73LM5%2FcmQ0Jt1r%2BQsMZ1XWcDGCkRevL%2FmyPg0hEW3QQnGu9SNumWujJNK7tkULOLjhDb3vO0BpHTD4E%2B6DTgFOSMAAb0hk%2FJA0R3MqOKGikRKQBsO%2FBjv9CYXuy1ZGVpkVqoDUwbvfhJafNXujHw2QvyKOn49PiPPE9fSpDOy9S%2FFBDqLzqxvkNLMYG0sjHJt24q9mPi06WwnHqCIjRyHAOBe9aH1TvbFJzgvfweujnJ9JvVLwThxKOBL%2BozntZAmZAqQZjBUtnirrUrMQNo6u6YslR24n1NyyrE1s%2B5vusG8fspToaF2TDpxHwVgnXhDt8YkNIwDUjLWU7B%2FT2nKw3dOZlxWAQryJizOJeBot82fg4r8jujwsVmETdZcYnlfcUvGgLbKUdYKpQcsPdCA24H0AOYOaKt4QF0GHWq%2BlN1oC9c26fCnZpZeHi7xMC2JWedJiVj0no4BtkVDeVpe2MdBI%2F27mOb7EJ5iK3tMnl6iTiD3QSLTXe27IZYMHMvrKbKXwVgn0XHj49KTrjuDRSvUMCwMOpvEnxmTmepZ%2BTKfNd3jNjxIg4Ft48KxDC67IHBBjqpAQwYiPK%2BTuDay7ukIFXvGI2LnwyhP95EVVKpVrupkPlNImuFbA2I%2FQPuOdx3U8RoNNfCHoV1XZtRyW6VSmoLobQ4cSxB86s%2B4FTq5kUd9Icts%2BPzPzfTNTEU1VLiPbh2omQfWUXGZiBlh7LN3COafUaw%2FPwnLn65wONPuyV6aEM%2Fn9CVeHCC9pGS252NmQZ8hkNDq6mui9WSP4oXIIY0UzxACV%2Ffz21M20M%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20250511T110532Z&X-Amz-SignedHeaders=host&X-Amz-Expires=3600&X-Amz-Credential=ASIAR3VDDKJJEJXMOYO6%2F20250511%2Feu-west-1%2Fs3%2Faws4_request&X-Amz-Signature=d12cdb48505ab56ab516f40b2033758e18b6c40514007f7720d8f36e43be3879",
            ad_account_id=5,
            report_type="spAdvertisedProduct",
            campaign_type="SPONSORED_PRODUCT"
        )
        from amazon.services import get_data_for_graph
        get_data_for_graph(user_id=5, amazon_seller_id='A26GG6KRQ84D7L', start_date='2025-04-05', end_date='2025-04-12', asins=None, graph_data_type='TRAFFIC', prev_end_date="2025-04-12", prev_start_date="2025-04-05")
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
