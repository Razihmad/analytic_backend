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
            url="https://offline-report-storage-eu-west-1-prod.s3.eu-west-1.amazonaws.com/473f30da-a40e-4e5c-94a5-78335db7e936-1747549790065/report-473f30da-a40e-4e5c-94a5-78335db7e936-1747549790065.json.gz?X-Amz-Security-Token=IQoJb3JpZ2luX2VjELb%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCWV1LXdlc3QtMSJHMEUCID%2B9e%2BFeFzZTVqdUKrb9c0i9bjNF0OMCxLDlECQvO1mBAiEA8310W0YPz9Jt1NEdlNYKDLO0wl5XGoHdLb5MFShDbsoq4QUIbxACGgwxMjgxMTczMzA1MTQiDFWpblGB7S%2BHDOB1%2Byq%2BBSoPmV%2FwgFi4Cvld7hr9PHDONmbHoNyxfhNUp6CWaNS12R7qQg%2ByyPn9ySUMbcRi8iZMJid6m1WK%2BL%2FiXruP6FU510sE%2FSn7cWQGtKPitpVfebHGbQBTYuU6OpXOfKg0NKWv0vgIY4a43A1dVT58p1Db6mHuTpXAhzJW8Baj7QATFjYg3KLjhUqnJ4SEJifKKxKPd5Wk%2BSb5x9WKA%2Fl5Kk1TiPDcNWf4MTc7E44AfiLSPsdnoD%2B%2Ft0vZ2o%2F9RWa%2By9xvh9A9neGK2NIGxn0rUrRNMvCo8Bv9i33VIdEQkE2mzGGp9mIabawCUzD%2FMzz2MAkTTxABuPAqEEo1IC058jIcvgzViiq4ski0LObpHVf2Ku2bcOl1hIQWGiwsW%2F09%2BrPz50iDqpI3R3BvVVqSTXz8xd8ATEEg4N%2FP8KRj6Zvp5qe02USa0GxzuryB7mt8XS7V0fRFDRcZsKsLHfooIQ8NiS7KHmyy9yzcFBh%2BYeV1wZnbTg38HvJYu7tdt%2FBCAW0WtWoQFOB8JaJQL6eMtHS%2F640veZmSYEAmMN8%2BEBq%2Bn4xgh9N0u2aGhVxEAwa1XFvjiHfrmgZbbvU8yEhX607kZqvCM5FqowLBXq92ljOvtsUPy%2Biy9avvwL5w3esGNKGjdYKHZEBksSE%2BxO7A3bYhqTSuk28WAdIbUSI1lYj4nIgUH0vv1R0ZDdt3gQhGgiNrGJXuLGXKLU%2BhFb1kaLDm5DbVhc4s986p8d%2FuTV7L%2F8DFm34ZHTEn%2Fjt12qIpObwUpPKDUHkUMc9oQseuoXcRdYpZNJwGPRZ6eRNhOpOXGbklx9kTZ2Bi4p69PZBL6XjnEkgvtdFxHdHwD0ozdx0o54OCYcPGfjIM8%2BTkCqN%2FS7%2BzBSvo%2BUtLMuXKF%2BTsuL57Xgg9BQy0WI6BWEmw7bLwx4hq%2BPQYkQS3YLfY%2BjDD6KXBBjqpAcOr59Oro3XVak%2FBSYw2Gvv4kXz1lRuB9ajyhL5y1L1z6tdYdm28YJhVS056c1etw23Ekzc03Zhcd%2BO6ImVtU6QB6AFdtfl28mrpkReCza%2FavZaRuwYNe1U3OQJaL2LWi%2FUc2jc96Dr7jVJxfPGUKkWdLzle5aJ9L4NKUHA0jJAGVqVpFRrp26aCWRWsUZUbTyCK2VpZcWEYfCiM4ZWuZ%2BnxGuVo3%2Ff5Z%2Fg%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20250518T065945Z&X-Amz-SignedHeaders=host&X-Amz-Expires=3600&X-Amz-Credential=ASIAR3VDDKJJONKRW3OA%2F20250518%2Feu-west-1%2Fs3%2Faws4_request&X-Amz-Signature=a643a887489fe91818d2799625704f740298f2c665bb1f53fcb11ff8900286dd",
            ad_account_id=5,
            report_type="spAdvertisedProduct",
            campaign_type="SPONSORED_PRODUCT"
        )
        # from amazon.services import get_data_for_graph
        # get_data_for_graph(user_id=5, amazon_seller_id='A26GG6KRQ84D7L', start_date='2025-04-05', end_date='2025-04-12', asins=None, graph_data_type='TRAFFIC', prev_end_date="2025-04-12", prev_start_date="2025-04-05")
        from amazon.tasks import testing_tasks
        testing_tasks.apply_async(queue="process_report")
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
