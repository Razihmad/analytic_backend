import logging
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

import utils.datetime as dt
from amazon_ads.services import create_negative_keyword, create_portfolio, fetch_ads_data_by_date, get_and_serialize_campaign_report_data, get_and_serialize_serach_term_report_data, get_negative_keywords, get_portfolios, process_campaign_sb_report_file, start_fetching_amazon_ads_data
from base.decorators import handle_exception
from base.response import status_200
# Create your views here.

logger = logging.getLogger(__name__)


class FetchAdsReport(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @handle_exception
    def post(self, request):
        amazon_seller_id = request.data.get("amazon_seller_id")
        user = request.user
        start_fetching_amazon_ads_data(amazon_seller_id=amazon_seller_id, user=user)
        return status_200(message="fetching data", data={"message": "Fetching ads report data."})


class FetchAdsReportByDate(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @handle_exception
    def post(self, request):
        amazon_seller_id = request.data.get("amazon_seller_id")
        user = request.user
        start_date = request.data.get("start_date")
        end_date = request.data.get("end_date")
        fetch_ads_data_by_date(user_id=user.id, amazon_seller_id=amazon_seller_id, start_date=start_date, end_date=end_date)
        return status_200(message="fetching data", data={"message": "Fetching ads report data."})


class UploadCampaignReportFile(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @handle_exception
    def post(self, request):
        file = request.FILES["file"]
        sales_date = request.data.get("sales_date", str(dt.now(with_tz=True).date()))
        amazon_seller_id = request.data.get("amazon_seller_id")
        process_campaign_sb_report_file(file=file, amazon_seller_id=amazon_seller_id, sales_date=sales_date, user_id=request.user.id)
        return status_200(message="Data Upserted successfully")


class GetCampaignReport(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @handle_exception
    def post(self, request):
        start_date = request.data.get("start_date", str(dt.now(with_tz=True).date() - timedelta(days=8)))
        end_date = request.data.get("end_date", str(dt.now(with_tz=True).date() - timedelta(days=2)))
        amazon_seller_id = request.data.get("amazon_seller_id")
        campaign_name = request.data.get("campaign_name")
        campaign_type = request.data.get("campaign_type")
        data, cumulative_data = get_and_serialize_campaign_report_data(
            user_id=request.user.id,
            amazon_seller_id=amazon_seller_id,
            start_date=start_date,
            end_date=end_date,
            campaign_name=campaign_name,
            campaign_type=campaign_type,
        )
        return status_200(message="campaign report fetched", data={"data": data, **cumulative_data})


class GetSearchTermReportData(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @handle_exception
    def post(self, request):
        start_date = request.data.get("start_date", str(dt.now(with_tz=True).date() - timedelta(days=8)))
        end_date = request.data.get("end_date", str(dt.now(with_tz=True).date() - timedelta(days=2)))
        amazon_seller_id = request.data.get("amazon_seller_id")
        data = get_and_serialize_serach_term_report_data(
            amazon_seller_id=amazon_seller_id,
            start_date=start_date,
            end_date=end_date,
            user_id=request.user.id,
        )
        return status_200(message="search term report fetched", data={"data": data})


class TestAccount(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]

    @handle_exception
    def get(self, request):
        logger.info(request.data)
        return status_200(message="test account", data={"message": "Test account", "data": request.data})

class CreateCampaign(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @handle_exception
    def post(self, request):
        logger.info(request.data)
        amazon_seller_id = request.data.get("amazon_seller_id")
        campaign_name = request.data.get("campaign_name")
        campaign_type = request.data.get("campaign_type")
        campaign_budget = request.data.get("campaign_budget")
        campaign_budget_type = request.data.get("campaign_budget_type")
        campaign_start_date = request.data.get("campaign_start_date")
        campaign_end_date = request.data.get("campaign_end_date")
        campaign_bid_strategy = request.data.get("campaign_bid_strategy")
        portfolio_id = request.data.get("portfolio_id")
        targeting_type = request.data.get("targeting_type")
        return status_200(message="campaign created", data={"message": "Campaign created", "data": request.data})


class CampginPortfolio(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @handle_exception
    def post(self, request):
        logger.info(request.data)
        amazon_seller_id = request.data.get("amazon_seller_id")
        portfolio_name = request.data.get("portfolio_name")
        policy_name = request.data.get("policy")
        portfolio_budget = request.data.get("budget")
        start_date = request.data.get("start_date")
        end_date = request.data.get("end_date")
        in_budget = request.data.get("in_budget")
        currency_code = request.data.get("currency_code")
        state = request.data.get("state")
        user = request.user
        data = {
            "name": portfolio_name,
            "budget": {
                "amount": portfolio_budget,
                "currencyCode": currency_code,
                "policy": policy_name,
                "startDate": start_date,
                "endDate": end_date,
            },
            "inBudget": in_budget,
            "state": state
        }
        create_portfolio(amazon_seller_id=amazon_seller_id, user=user, data=data)
        return status_200(message="campaign portfolio created", data={"message": "Campaign portfolio created", "data": request.data})
    
    @handle_exception
    def get(self, request):
        logger.info(request.data)
        amazon_seller_id = request.data.get("amazon_seller_id")
        user = request.user
        portfolios = get_portfolios(amazon_seller_id=amazon_seller_id, user=user)
        return status_200(message="campaign portfolio fetched", data={"message": "Campaign portfolio fetched", "data": portfolios})


class NegativeKeyword(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @handle_exception
    def post(self, request):
        logger.info(request.data)
        amazon_seller_id = request.data.get("amazon_seller_id")
        campaign_id = request.data.get("campaign_id")
        ad_group_id = request.data.get("ad_group_id")
        keyword = request.data.get("keyword")
        match_type = request.data.get("match_type")
        state = request.data.get("state")
        user = request.user
        response = create_negative_keyword(
            amazon_seller_id=amazon_seller_id,
            user_id=user.id,
            campaign_id=campaign_id,
            ad_group_id=ad_group_id,
            keyword=keyword,
            match_type=match_type,
            state=state
        )
        if not response.get("negativeKeywords", {}).get("error"):
            return status_200(message="negative keyword created", data={"message": "Negative keyword created", "data": response})
        return status_200(message="negative keyword creation failed", data={"message": "Negative keyword creation failed", "data": response})


    @handle_exception
    def get(self, request):
        logger.info(request.data)
        user = request.user
        amazon_seller_id = request.data.get("amazon_seller_id")
        campaign_ids = request.data.get("campaign_ids", [])
        ad_group_ids = request.data.get("ad_group_ids", [])
        data = {}
        if campaign_ids:
            data["campaignIdFilter"] = {"include": campaign_ids}
        # incomplete yet TODO: 
        negative_keywords = get_negative_keywords(
            amazon_seller_id=amazon_seller_id, user=user, campaign_ids=campaign_ids, ad_group_ids=ad_group_ids
        )
        return status_200(message="negative keyword fetched", data={"message": "Negative keyword fetched", "data": negative_keywords})

    @handle_exception
    def delete(self, request):
        logger.info(request.data)
        amazon_seller_id = request.data.get("amazon_seller_id")
        user = request.user
        campaign_ids = request.data.get("campaign_ids", [])
        ad_group_ids = request.data.get("ad_group_ids", [])
        delete_negative_keywords(amazon_seller_id=amazon_seller_id, user=user, campaign_ids=campaign_ids, ad_group_ids=ad_group_ids)
        return status_200(message="negative keyword deleted", data={"message": "Negative keyword deleted", "data": request.data})