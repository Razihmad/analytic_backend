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
        download_file_and_process_report_data(
            user_id=9,
            report_id='59ae20f7-78c8-45c9-b4da-51043c59c558',
            url="https://offline-report-storage-eu-west-1-prod.s3.eu-west-1.amazonaws.com/f2c696ce-2086-48af-b8ab-47d5bd6ca2cc-1753288316450/report-f2c696ce-2086-48af-b8ab-47d5bd6ca2cc-1753288316450.json.gz?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEPD%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEaCWV1LXdlc3QtMSJGMEQCIE%2FAA5e6ICbRX%2BHBfdMdsrEKLio6fpCdcj4p67r4OiybAiAyhJ6GiR3LrDYhq0Rn0Aw5AMNcjIA%2BnsMlfWyHoLIJUyrhBQgZEAIaDDEyODExNzMzMDUxNCIMB9OFKGzOieIJ07ddKr4FHIiYEc0MTQHBEDtidjM3jqytzUidcaPZQ3kJ%2FOFIfd4p09T8%2By7p2TAR5dl%2FVrJg31ASXxVCK4Ru8%2F2Qdo%2Fn6SgO9PXHKZpKjC8UBT%2BVvFYAqTOMkq1gLHl9WeCzu6JvF0JaQUjaFjdygY4ZPljIsmqZ0di4yogd4rcRqBW7eTsnNLR7qytwQxwcEUOTZ0LK63X3mOYJEZFCP1tITPxFGvMQm1l0ZBPZYsi95NU%2Fz5kghSUoNtIk%2BDfNY5L8J4eJmZ3%2BNcWoOMaScqYf%2BYNqRLcyVhNpu6iBZBmvO%2B4GOcQP9If4R%2F5%2FTSRrVU%2FUvblUlbitb0j2%2FkE8sXaLazVEN6gKP7IdFNrE%2F39tZnsX3hsCJtAfR%2Bii2UzSsdy9Y3zrvEvCnJDtjU1r6xqLn4aCt74PF5OYjOs7EGbGZYlP16n5Dj4H%2FyFV%2FKjw2XlDATgQ9mxJL1jJavjuT59sk1uwI6br4%2FChb0FVNp1NtfrGxcB%2FRuI4s%2FDmjizpbqZ70HYfFPsQn5qH1fpDxfztRZ%2B4CPeMmXkd3jb9rcdBMAV6IQ5yHlJsR6CrkEX20wlvRO2gnVJv4mmghcZvVqBKiTSQWpXj%2B60NOR%2FoGGZtR4cB2CoIAqNyBn%2Bc3R%2BqwhE%2Fx7sQ%2F8OMLp%2BYQDo9fQIsJYOiwvI1yQx5wCFK%2FoZkNP5%2FBAaL0hG%2F0BIwacF21pi3K0SmtdkZMKGD%2F4JllstSZirTLzua5DVmDvzZgJuuENV0VRadOCDRn0vCsk38JN3Rdw3NKRZ7yIs5zitOrHW8b1Q9yhUJaRT3u50ZnpybRbgjVRc%2BXwemfR41S%2BaF0Cfh3BzP%2BxYgdYxsaMW3UWRAgFWreGVq4lX%2FEXOUJT0vGADHMhyxL5%2FoLnUNrMC2Nyqe9qsrI%2F2LlvdNytmSvvOw6DgKnX1mnM%2FmgI76thBcrfzTMJCMhMQGOqoBTwfnYi1M%2F5zOrNX5Za2Jj2KF5Gc1fb%2FidBSJyZuRHBZCmvyj0YdkKgji58o3texVHNLTYr3LzBs2jUerzTnKGbRHdjYZRM7ZdNqwqLzYcyd8BaVEpmI%2BqbKy2kvp4wABP0LvhLYLEjdjAH8TFaTWksyckhuN8IzbdEEeT6kFXk8qrsr1p1D9EHm7E%2FVe42W%2BCV%2FcBqr870ugtFVtl2N8yD%2BX1jEh%2FCR7E7I%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20250723T164651Z&X-Amz-SignedHeaders=host&X-Amz-Expires=3600&X-Amz-Credential=ASIAR3VDDKJJP4BQDHXC%2F20250723%2Feu-west-1%2Fs3%2Faws4_request&X-Amz-Signature=4a7d38eaa6f3ee0ab368f744d1a24f17b078d486fe714d57e173864259dab629",
            ad_account_id=26,
            report_type="spTargeting",
            campaign_type="SPONSORED_PRODUCTS"
        )
        # # from amazon.services import get_data_for_graph
        # # get_data_for_graph(user_id=5, amazon_seller_id='A26GG6KRQ84D7L', start_date='2025-04-05', end_date='2025-04-12', asins=None, graph_data_type='TRAFFIC', prev_end_date="2025-04-12", prev_start_date="2025-04-05")
        # from amazon.tasks import testing_tasks
        # testing_tasks.apply_async(queue="process_report")
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
        logger.info(f"{asins=}, {start_date=}, {end_date=}, {amazon_seller_id=}, {user.id=}")
        product_analysis = get_product_analysis(
            user_id=user.id,
            amazon_seller_id=amazon_seller_id,
            start_date=start_date,
            end_date=end_date,
            asins=asins,
        )
        return status_200(message="Product Analysis", data={"product_analysis": product_analysis})
