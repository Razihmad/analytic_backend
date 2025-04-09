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
            report_id="ceb86cbc-8cc8-466a-bb82-d9891c8ce042",
            url="https://offline-report-storage-eu-west-1-prod.s3.eu-west-1.amazonaws.com/392b22db-11b1-423d-a5ae-424ea041b4e8-1744207175192/report-392b22db-11b1-423d-a5ae-424ea041b4e8-1744207175192.json.gz?X-Amz-Security-Token=IQoJb3JpZ2luX2VjEBYaCWV1LXdlc3QtMSJIMEYCIQCl98QhEIuNz%2F%2BckOQSH%2BMUF2mj%2Bx8NIfjOwd0%2FegxiBgIhAP92avmmbuuD%2BJna87QuZLGJh8fHNsGE7hM6a3Zqm6QvKuoFCI%2F%2F%2F%2F%2F%2F%2F%2F%2F%2F%2FwEQAhoMMTI4MTE3MzMwNTE0IgyP8Iz7tCO1zj1UuTYqvgVPoXUP9t%2FskFJWHatKtiBRk9iklis%2BQrCnzN%2BPUAvsXimiNXIlk9NKhA5sDFFnk8vTsnguhN7n7488wujkuSH9h%2FHEzpB0vgDBlSh4EU9TtILTb2wyVJZjp8IMQqsWlFXO5eny36XIRAF0EJNxyjJZCHTJA1htujF2k9xWNNlMjncswzhQTbrfBiVZhGz%2FmnEykUCmWQRYrIIGoE2CrjzLezXsCp2ZijnG5ak3JvasHndDK9VFVuCtELCjhUvMV5dN8%2Fg69J0RhtUDHzkBv7o9zc7k%2BjCAymxDlHlcguhzI6NWwm0OG%2F2L3LdjaMOrSDU9oBqtCD8ujgqJrB8Qu8RvesLVs8HfvA1RFF3LrRUrWHojDdAZqXR3esCV383EMp2BtE5Z4mn6WW3h%2BgSoRAoKHNhL%2FI%2BLkeyetKxxKFImIPRUBifykRnVg7np45OkphtCKJXxpzYn4MVMDzoKFTIEq0YYtLT2QJZ49vF1REuVOCWNqjkJ5nRSW9jGVXYqGpX40KSLi%2B3ZhSWnIJayVkKbWRrKjElndltj2SyLpOW%2FPmeNSQSH2TBbhlnEBrOuiXhDtKAGitMYUmBFl1tOEglL%2BLk77KsGuitVnKMFG0s07dNl%2Fxzd2r6Ls0reLGatOJwUe5r0NGmmUKfIxw3N6hA6pPcAQpqQrcpYdGhZGCvLSiof3%2FHUDF2kVyzg1otPglrjT%2FqeWDdZ%2Fnx1R5LnedXoWXLY249GDElfD3cJ2TfZzDSEWRvVV7Y5NzMyjbDHjIV0pq9ic9etBTF%2FEvN5IK1imjC%2BNJQWp7d%2BQ706G180vxvvSBSF2RKqU9aquAWHMH5C4huIQeKN7ObR3fHtMzlfHWUSc0gwOqkMH%2Bgrx58GxKhbDwCHx37z29TZ91TSux%2FLehn0KKfbzwd8zjTkXfqRDGEIIIa6LenKDeu5izAwoO3ZvwY6qAE8RkKufdltjXTdAgqtCXUg7CC8R%2B76xFH%2BGIW8c8euU5VnhfPP7cAzSdG65td6gxNo%2BUT%2BWw%2BBfHtxuwy6VnQShRFs7BXj0kNkchHxKkFDasHkKAP51Kcnd2LTU8JBXaHs%2Buet19%2Br0OGXancLU1rgOxnGn4NqfCuEFcMmTGH9TNms9CUy%2FQBi7HQJrbGzAbD7f2XS3Q%2BO70OGFfIEGMgdP77%2FMWLC%2FxQ%3D&X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Date=20250409T140425Z&X-Amz-SignedHeaders=host&X-Amz-Expires=3599&X-Amz-Credential=ASIAR3VDDKJJNSYJLFN5%2F20250409%2Feu-west-1%2Fs3%2Faws4_request&X-Amz-Signature=8289da81ad1317c4a5ba898d1981318c8052e69aaee22c7b24380676c777057e",
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
