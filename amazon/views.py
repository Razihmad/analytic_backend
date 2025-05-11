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
            url="https://offline-report-storage-eu-west-1-prod.s3.eu-west-1.amazonaws.com/59ae20f7-78c8-45c9-b4da-51043c59c558-1745684680863/report-59ae20f7-78c8-45c9-b4da-51043c59c558-1745684680863.json.gz?X-Amz-Security-Token=IQoJb3JpZ2luX2VjELD%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCWV1LXdlc3QtMSJIMEYCIQDI%2Ft73fKoTxQ4lV%2BzC%2Be%2F4Tl%2FrN996Qm1MEa6wx7E4iAIhAP4j7oSkPhZKCHxdfWMB3HkxJQ6%2FwjW7m%2B3VqC0R2mVyKuEFCEkQAhoMMTI4MTE3MzMwNTE0IgxtlF0esXiM7CbP%2F3cqvgX0Imoab52VeFY%2FQ%2BO3NSiuCQ3VKqlRmOsDPr8Ju4sF3ud5cbmkb3sYN0Dy2ZNZUfPKVLV2EoW%2F1VpId44E6TaF2JK58rBpJHChHMQTNB439FjZCQW2ZWoyKkbrPXUjEPRcZcdeDCA%2FZoKr1KaaQ8UKgZJEEfx7IAyzWL374m49bFVTD9vAuEbbDyywEZJTrVcqOrpQBld1RRMYNcNM44E7eJlFHQz0Bc7rTKm0WKfjpdNFBUdc9tovadXdMpSCnZuhTUIpKRm7JQGxeKAgsDaltRdIFsTnJAouqdwb3Gi%2FT3Eg4TgkIwWKLo4rZax1kMHPOtJbgklKTUUWDhvPBERzYLeWkFHtoDQDjP1M2RvXla6MbRx8DpJUa41DFe%2B7TdFMZpSZCWcD2gZZH0%2FvMuSVzlEIooxXl0RKL%2FC3ucG08Q%2B3cgHOT1iRs8w4lHoqeU8tKG%2FXpWGCQfwAzhc07ZVeSFrAVYAvtmVj2FZH3eR%2BjIL5d4KL3cQ0gMAkiHrxAZ0MayN72TCP2mHGaJJuNhRlrP5RQ0fJ0WazTk1Ty878yTeCoWocQ5BS1vBJnm5ELe%2BzrsJN5nlqnbAP023HvsVDvHFuJa5NtWFsPI9exGWB4SQRpfCmrukfJsmhD6siyaFwdhhTWJkLhfOAtisWctneac0FmQyKVuXh0bo7EBeHvVidjcO4qot9q9QEC5EWOaytMbA5O5eyMiLjeAsfvhUYU9LGynlsiJ1pAJLzRJZgNAEP5MbZavibvwWBIfrbudf0ZEOlHLiY9pelQ8ERYKJ%2BhZTYdnNHwzBSoZgcR%2B5%2BiuxxF7JqJ1hins9wUznVr%2BABdTPri3vDDdWHsUpDoiXKq%2B7AZskfjT5Z0ldokIQiUSGMZ4hvI9WCe%2B3q%2BNi1CIbRSkgLELJbnB0d%2FM9nvjO7auwDytxTcGjoEUQHBGkwzIa0wAY6qAGPQGs4ckdyWxC1ss5J2kKJ4rSEjXdb9WfYJCBYWiZyOzCQhFfzu6hXJtwnGjytAeulBMjtdZq6PMnDFihc4gv20WibJeUqKsmoH%2FgRJ8gnes9YJT6dHdUBcuUcNP%2BZXH%2BEU7un9SzlqPzhBqiKcCX5%2BBJ8qTDfIiIfmvvCPKp1OJ7Pw%2Ftml63I8j9Y0kn2ypOJzVV9e8a6w6nIJZv%2FPWQVmCW74mdtJPk%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20250426T164435Z&X-Amz-SignedHeaders=host&X-Amz-Expires=3600&X-Amz-Credential=ASIAR3VDDKJJD3MSOKC6%2F20250426%2Feu-west-1%2Fs3%2Faws4_request&X-Amz-Signature=cd50fc276d84508555471d67f08a516bfadb4a915e153d6c87cd926b3462fd1e",
            ad_account_id=5,
            report_type="sbCampaigns",
            campaign_type="SPONSORED_BRANDS"
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
