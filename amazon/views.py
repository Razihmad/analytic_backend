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
            url="https://offline-report-storage-eu-west-1-prod.s3.eu-west-1.amazonaws.com/b11456b8-21c2-4ca1-9708-b50c8ae4af71-1745665240436/report-b11456b8-21c2-4ca1-9708-b50c8ae4af71-1745665240436.json.gz?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEKv%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCWV1LXdlc3QtMSJGMEQCIB76C8MycEq%2F7AkGPT21VPAuBH31wPiZBqmy1VpEVActAiA8EKMRlYhIgHNK60XZ8vaG67lldoSAZrfMZ%2BMUdTAmCyrhBQhEEAIaDDEyODExNzMzMDUxNCIM9hL5Rh7%2BBq%2BAcJR0Kr4FyS8eikYPdxsGmRK322iBRErF6z51Qzd6qHbezCv3NsNWaj%2FZzPNiETV40WCMEC%2F%2B%2BCiHYbG2FQV7h3rfqvDka5NxVN5gVE1R7M8%2F9JymNJr5E6g0l%2BPkoGjUfeI4415YNqaZPGU7QIOSOgrxg71lT%2BkpkkAN47XY6rtAQF%2BWt9mK8n6bil0TRG89QOXGQEHB4Fetupb%2FG7MgxWeCU8Y3kJZut%2FdcGxRNO8y3e%2BMwu88IPKOF8dV79pHS2D2rb0hXXii9MqNWLxtsas3QvtcC%2BvkkXKR5oInwe7tfZq6eAn6dNnesRqf3T1yRWDT7VQ9GfTKHdEwBJGHCDXdnvpor6oE6QrMmey7W7AiFLgz%2F5rgBOIVLE84pVAtKngQGxQrMPuU3DQQWgks%2BecrtS2%2Bl%2FzFZ1QsVFukRuxxZ5%2BffjnCT7MD2l7%2BxIz%2FPXGK94hp9O1niCssqZHoIeCg5R6rTN8JfDC1OUjtxS1%2Fwnl7opzYF%2FA33BM7xD8OeuY5Iu6vN8rw7xyddBTIwAKljKUEv2YKWtSnaBieFh0Kn%2F%2Bxii3vuNtJL4ygvqKfmvtLhhvOc9kd7DPe3credDB6dYJZ2bK1siGHWWUzOpfQ29Kh9hil94UuUI61oEpWjf4pThE6i%2BXUPD0kAfVXCQIw5WE7lmfZQbCERg3QdUbRgsN8E8X4L0j6qv%2BXAacjP%2F%2Fli%2BFwb6f01h9m4tAq6pto36WnYH74KSotfH4mJPlHKQHBdvHvyAokJgNzJOw0HPezsuT8lxLzW5zAScua4EBnUSofPYfyTdgWTPYLh4OD7Hv6d04LBgcGJDHtIBpCeedgbKXKnKugtYAwMznKEFjH%2BlE3ZtC3oUzp99uTMfD6wjeYuyxeNL5nF4qxMP1xlaAJIhS8MtwFwHXD7YdAlw83DK5mTHA5x9km13MMvtsoHXLIzMPr3ssAGOqoBhpg6%2F6Z6GVGSvaqKP%2F9Xlt29C3tHRHxu18fsyKdPdNf8iBaGMvo%2F4NQ2sT75R2zULBZ6XoM%2FRwYOMzG0YW%2BiKIaage5faC5OAqpkmUBR4PgJ5vGTh5Uz6tuKdS%2BPG8efImVjKibzfBZMoav%2FXp7b7x7ZzlqoZg5%2BO2KWOkrtnlz%2FR62X%2BNa7IyhBCsXucwxIj7cGZdmPu3W71%2Fx2ob2VLoH1Hj2L11ydjHk%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20250426T113037Z&X-Amz-SignedHeaders=host&X-Amz-Expires=3600&X-Amz-Credential=ASIAR3VDDKJJA7SVVSLB%2F20250426%2Feu-west-1%2Fs3%2Faws4_request&X-Amz-Signature=5a820b8e5ad6dad46b70ea34feca6810788b68c3ba067f99d94efa0a792113c5",
            ad_account_id=5,
            report_type="sbCampaigns",
            campaign_type="SPONSORED_PRODUCTS"
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
