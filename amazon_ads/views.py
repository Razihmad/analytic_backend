import logging
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

import utils.datetime as dt
from amazon_ads.services import create_keyword, create_negative_keyword, create_negative_targeting, create_portfolio, delete_negative_keywords, fetch_ads_data_by_date, get_and_serialize_campaign_report_data, get_and_serialize_serach_term_report_data, get_and_serialize_targeting_report_data, get_negative_keywords, get_portfolios, get_targeting_graph_data, process_campaign_sb_report_file, start_fetching_amazon_ads_data, update_keyword
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
        search_term = request.data.get("search_term")
        campaign_name = request.data.get("campaign_name")
        keyword = request.data.get("keyword")
        ad_group_name = request.data.get("ad_group_name")
        match_type = request.data.get("match_type")
        query_params = request.query_params
        logger.info(f"{request.data=}, {query_params=}")
        data, aggregated_data = get_and_serialize_serach_term_report_data(
            user_id=request.user.id,
            amazon_seller_id=amazon_seller_id,
            start_date=start_date,
            end_date=end_date,            
            search_term=search_term,
            campaign_name=campaign_name,
            keyword=keyword,
            ad_group_name=ad_group_name,
            match_type=match_type,
            query_params=query_params
        )
        return status_200(message="search term report fetched", data={"data": data, "aggregated_data": aggregated_data})


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
        response, status_code = create_negative_keyword(
            amazon_seller_id=amazon_seller_id,
            user_id=user.id,
            campaign_id=campaign_id,
            ad_group_id=ad_group_id,
            keyword=keyword,
            match_type=match_type,
            state=state
        )
        if status_code == 207:
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
    

class CreateKeyword(APIView):
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
        bid = request.data.get("bid")
        user = request.user
        response, status_code = create_keyword(
            amazon_seller_id=amazon_seller_id,
            user_id=user.id,
            campaign_id=campaign_id,
            ad_group_id=ad_group_id,
            keyword=keyword,
            match_type=match_type,
            state=state,
            bid=bid
        )
        if status_code == 207:
            return status_200(message="keyword created", data={"message": "Keyword created", "data": response})
        return status_200(message="keyword creation failed", data={"message": "Keyword creation failed", "data": response})
    
    @handle_exception
    def put(self, request):
        logger.info(request.data)
        user = request.user
        amazon_seller_id = request.data.get("amazon_seller_id")
        data = request.data.get("data")
        response, status_code = update_keyword(
            amazon_seller_id=amazon_seller_id,
            user_id=user.id,
            data=data,
            content_type="application/vnd.spKeyword.v3+json",
            accept="application/vnd.spKeyword.v3+json"
        )
        if status_code == 207:
            return status_200(message="keyword updated", data={"message": "Keyword updated", "data": response})
        return status_200(message="keyword update failed", data={"message": "Keyword update failed", "data": response})


class NegativeProductTargeting(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @handle_exception
    def post(self, request):
        logger.info(request.data)
        amazon_seller_id = request.data.get("amazon_seller_id")
        campaign_id = request.data.get("campaign_id")
        ad_group_id = request.data.get("ad_group_id")
        asin = request.data.get("asin")
        campaign_type = request.data.get("campaign_type")
        user = request.user
        response, status_code = create_negative_targeting(
            amazon_seller_id=amazon_seller_id,
            user_id=user.id,
            campaign_id=campaign_id,
            ad_group_id=ad_group_id,
            asin=asin,
            campaign_type=campaign_type
        )
        if status_code == 207:
            return status_200(message="negative product targeting created", data={"message": "Negative product targeting created", "data": response})
        return status_200(message="negative product targeting creation failed", data={"message": "Negative product targeting creation failed", "data": response})



class GetTargetingReportData(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @handle_exception
    def post(self, request):
        start_date = request.data.get("start_date", str(dt.now(with_tz=True).date() - timedelta(days=8)))
        end_date = request.data.get("end_date", str(dt.now(with_tz=True).date() - timedelta(days=2)))
        amazon_seller_id = request.data.get("amazon_seller_id")
        campaign_name = request.data.get("campaign_name")
        ad_group_name = request.data.get("ad_group_name")
        match_type = request.data.get("match_type")
        query_params = request.query_params
        logger.info(f"{request.data=}, {query_params=}")
        data, aggregated_data = get_and_serialize_targeting_report_data(
            user_id=request.user.id,
            amazon_seller_id=amazon_seller_id,
            start_date=start_date,
            end_date=end_date,            
            campaign_name=campaign_name,
            ad_group_name=ad_group_name,
            query_params=query_params,
            match_type=match_type,
        )
        return status_200(message="targeting report fetched", data={"data": data, "aggregated_data": aggregated_data})


class GetTargetingReportGraphData(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @handle_exception
    def post(self, request):
        start_date = request.data.get("start_date", str(dt.now(with_tz=True).date() - timedelta(days=8)))
        end_date = request.data.get("end_date", str(dt.now(with_tz=True).date() - timedelta(days=2)))
        amazon_seller_id = request.data.get("amazon_seller_id")
        campaign_name = request.data.get("campaign_name")
        ad_group_name = request.data.get("ad_group_name")
        match_type = request.data.get("match_type")
        query_params = request.query_params
        logger.info(f"{request.data=}, {query_params=}")
        data = get_targeting_graph_data(
            user_id=request.user.id,
            amazon_seller_id=amazon_seller_id,
            start_date=start_date,
            end_date=end_date,
            campaign_name=campaign_name,
            ad_group_name=ad_group_name,
            match_type=match_type,
            query_params=query_params
        )

        return status_200(
            message="targeting report graph data fetched",
            data={"message": "Targeting report graph data fetched", "data": data}
        )
