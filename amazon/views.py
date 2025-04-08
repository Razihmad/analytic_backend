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
            report_id="f57813c1-e9f5-4097-9ad8-362b2467e66b",
            url="https://offline-report-storage-eu-west-1-prod.s3.eu-west-1.amazonaws.com/94ec7428-26e8-4951-a613-2f37af90d84f-1744139398692/report-94ec7428-26e8-4951-a613-2f37af90d84f-1744139398692.json.gz?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEAMaCWV1LXdlc3QtMSJHMEUCIQD0x6ytXsHyO5vgT6cBlYrGdMcvRoOX9Vi4m8lWfbhMPQIgXazyfaO2Cn4I0FBtgItaH5ZVFnzQrI1065nUYuAyr%2Fcq4QUIfBACGgwxMjgxMTczMzA1MTQiDAxntNfoKJ4ZKsMVeSq%2BBQigMGwnFcymzdQHr7KFpHLWHykYvxorqBzrM%2BS%2FMMACE7mSP6la8JGQlV8iT4HSjhE14r4OTt6Zv7f%2F94%2Fn7flwaA1rrX0kDXErcQzBqkEjNXomMIR0ih6HwXJdZ3MXamuNa8%2B4OkJY4jo99wsTILnIV3dwOWuOMmfg2U%2B%2BUwQU4FBONOoSPtkUpGJcO5C7Ku4PxrlphehdCRmc9CRuVe%2FDah%2BQXfLBJJ61S5roQuOp0ucpf%2Bd9%2FXi0MnOETbJsiIiYm5qBjBIOHFyxf%2BtdrwOCsPyxBflWEj15ZbsjX9MMA56lgwbcifyF5tzf4ktTarvCEVfyBxb60G%2FARi84IAdQY1BCG6L05uHIPldNOxBPT8Swz589Glj7rhaFQJB6crkb3LZwDs3eZGTfJj0xGh68wqPSj5Rf%2FTm%2F%2Bah3Z1LMjCFeZFNai61XUuODsPY0epMrt5DOV%2BUN19ilLxkCqOss0h2lKaEQ8vMjI%2FJBeYWB0TWBDLpN2smu431P63AZks4uC8Z%2F3J0nhsOPpQZchjDUH%2Fyg0lmc3s8gVeHd2HqGfkd3p5cZ3ZBYiWxIYNdK2hAug0PZq6XxLiRmrTuRLhwBkYMrFWywLNzdYNVZjOAo2NrZXamKMUzRvJZxcn4OBW2E%2BF6s5ZV58xbhLHupBnW6c95W0AuGzmatCxvaJ1%2FIEwziz7kyrSHcQcaiSm4kwJPWGAIS%2BOu90ry1zOQbIYkqGwWW1ZuUSrYIi67jxucjLXottbuK4J8px8FFBpgJPMgpJCtZyf0ABCwwY81Mjo9YXGcpzTW6NniahE6luhjhZg%2FfXJU9HqYP3RMey7%2FV2QBfDMoiWh66AekWwiuEVGpd7GLim7cRG%2FgMNaRFs7INA3t9bXF64%2B%2BBNM8M%2BRkkXz7Ovsp3bXCstCVDsaCl3kTXvVziF9gM%2FMSLbyqCVDC%2B59W%2FBjqpAY3czvn7DPLlT10XEc1WC3rcn4iq5xHugLFOBEJ2mMjvKxtldlDOSGzjQRx5RN7mzRrM%2FVGmRjvmW%2BWQkmw40BFEPY%2BaFPf364pzSMmI0FdCTtYDEgM8Qa2JnmGXIjgsGgW3cOATg%2BDZCwoQ%2BDEjpNWI7KUrUrVdKY8RGd2YpIUfQyn8Xj8IXO9GlVtespolO9veXeY1dzFdJr25vELoSDbbtqS5xEEuwd4%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20250408T191451Z&X-Amz-SignedHeaders=host&X-Amz-Expires=3600&X-Amz-Credential=ASIAR3VDDKJJEDBFIZ5K%2F20250408%2Feu-west-1%2Fs3%2Faws4_request&X-Amz-Signature=dd49a0ac35250628e8fe9928f07e5d087caade83e39b9bddbd66c7a20de45ff7",
            ad_account_id=5,
            report_type="spAdvertisedProduct",
            campaign_type="SPONSORED_PRODUCTS"
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
        report, performer_asins = get_sales_report_data(
            user_id=user_id,
            amazon_seller_id=amazon_seller_id,
            start_date_str=start_date,
            end_date_str=end_date,
            asins=asins,
            prev_start_date=prev_start_date,
            prev_end_date=prev_end_date,
        )
        return status_200(message="Sales Data", data={"report": report, "performer_asins": performer_asins})


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
