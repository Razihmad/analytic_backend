from enum import Enum


class AdsReportTypeId(Enum):
    SP_ADVERTISED_PRODUCT = "spAdvertisedProduct"
    SP_CAMPAIGN = "spCampaigns"
    SD_ADVERISED_PRODUCT = "sdAdvertisedProduct"
    SD_CAMPAING = "sdCampaigns"
    SB_CAMPAIGN = "sbCampaigns"
    SP_SEARCH_TERM = "spSearchTerm"
    SB_SEARCH_TERM = "sbSearchTerm"
    SP_TARGETING = "spTargeting"
    SD_TARGETING = "sdTargeting"
    SB_TARGETING = "sbTargeting"


class GroupBy(Enum):
    CAMPAIGN = "campaign"
    ADVERTISER = "advertiser"


class AdProduct(Enum):
    SPONSORED_PRODUCTS = "SPONSORED_PRODUCTS"
    SPONSORED_DISPLAY = "SPONSORED_DISPLAY"
    SPONSORED_BRANDS = "SPONSORED_BRANDS"


class Granularity(Enum):
    DAILY = "DAILY"
    SUMMARY = "SUMMARY"


class ReportStatus(Enum):
    SUCCESS = "SUCCESS"
    PROCESSING = "PROCESSING"
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"


class CampaignStatus(Enum):
    ENABLED = "ENABLED"
    PAUSED = "PAUSED"
    ARCHIVED = "ARCHIVED"


CAMPAIGN_REPORT_COMMON_COLUMNS = [
    "date", "campaignName",
    "impressions", "clicks", "cost",
    "campaignStatus", "campaignId",
]
SP_CAMPAIGN_REPORT_COLUMNS = CAMPAIGN_REPORT_COMMON_COLUMNS + [
    "sales14d", "unitsSoldClicks14d", "purchases14d", "spend", "costPerClick", "clickThroughRate", "campaignBiddingStrategy"
]
SD_CAMPAIGN_REPORT_COLUMNS = CAMPAIGN_REPORT_COMMON_COLUMNS + ["sales", "unitsSoldClicks", "purchases"]
SB_CAMPAING_REPORT_COLUMNS = SD_CAMPAIGN_REPORT_COLUMNS

CAMPAIGN_COLUMNS = {
    "SPONSORED_PRODUCTS": SP_CAMPAIGN_REPORT_COLUMNS,
    "SPONSORED_BRANDS": SB_CAMPAING_REPORT_COLUMNS,
    "SPONSORED_DISPLAY": SD_CAMPAIGN_REPORT_COLUMNS,
}

CAMPAIGN_TO_REPORT_TYPE_MAPPING = {
    "SPONSORED_PRODUCTS": "spCampaigns",
    "SPONSORED_BRANDS": "sbCampaigns",
    "SPONSORED_DISPLAY": "sdCampaigns",
}

TARGETING_TO_REPORT_TYPE_MAPPING = {
    "SPONSORED_PRODUCTS": "spTargeting",
    "SPONSORED_BRANDS": "sbTargeting",
    "SPONSORED_DISPLAY": "sdTargeting",
}
SEARCH_TERM_TO_REPORT_TYPE_MAPPING = {
    "SPONSORED_PRODUCTS": "spSearchTerm",
    "SPONSORED_BRANDS": "sbSearchTerm",
}

CAMPAIGN_TO_ADVERTISED_PRODUCT_REPORT = {
    "SPONSORED_PRODUCTS": "spAdvertisedProduct",
    "SPONSORED_BRANDS": "sbCampaigns",
    "SPONSORED_DISPLAY": "sdAdvertisedProduct",
}
SP_ADVERTISED_PRODUCT_COLUMNS = [
    "date",
    "costPerClick",
    "advertisedAsin",
    "impressions",
    "clicks",
    "cost",
    "spend",
    "sales7d",
    "sales14d",
    "unitsSoldClicks7d",
    "unitsSoldClicks14d",
    "purchases7d",
    "purchases14d",
    "campaignName",
    "campaignId",
    "adGroupId",
    "adGroupName",
]

SD_ADVERTISED_PRODUCT_COLUMNS = [
    "date", "impressions", "clicks", "cost", "sales", "promotedAsin", "purchases", "unitsSoldClicks", "campaignName", "campaignId", "adGroupId", "adGroupName"
]

AD_PRODUCT_COLUMN_MAPPING = {
    "SPONSORED_PRODUCTS": SP_ADVERTISED_PRODUCT_COLUMNS,
    "SPONSORED_DISPLAY": SD_ADVERTISED_PRODUCT_COLUMNS,
}


class GraphDataType(Enum):
    REVENUE = "sales"
    TRAFFIC = "traffic"
    IMPRESSIONS = "impressions"
    ORDERS = "orders"
    SPEND = "spend"
    CLICKS = "clicks"
    AOV = "aov"


SEARCH_TERM_REPORT_COLUMNS = [
    'impressions', 'clicks', 'cost', 'purchases14d', "sales14d", "unitsSoldClicks14d",
    'keywordId', 'keyword', 'date', 'searchTerm', 'campaignName', 'campaignId',
    'keywordBid', 'adGroupName', 'adGroupId', 'keywordType', 'matchType', 'targeting'
]

SB_SEARCH_TERM_REPORT_COLUMNS = [
    'impressions', 'clicks', 'cost', 'purchases', "sales", "unitsSold",
    'keywordId', 'keywordText', 'date', 'searchTerm', 'campaignName', 'campaignId',
    'keywordBid', 'adGroupName', 'adGroupId', 'keywordType', 'matchType'
]

SEARCH_TERM_REPORT_COLUMNS_MAPPING = {
    "spSearchTerm": SEARCH_TERM_REPORT_COLUMNS,
    "sbSearchTerm": SB_SEARCH_TERM_REPORT_COLUMNS,
}


SP_TARGETING_REPORT_COLUMNS = [
    'impressions', 'clicks', 'cost', 'purchases14d', "sales14d", "unitsSoldClicks14d",
    'keywordId', 'keyword', 'date', 'campaignName', 'campaignId',
    'keywordBid', 'adGroupName', 'adGroupId', 'keywordType', 'matchType', 'targeting'
]

SD_TARGETING_REPORT_COLUMNS = [
    'impressions', 'clicks', 'cost', 'purchases', "sales", "unitsSold",
    'date', 'campaignName', 'campaignId', 'adGroupName', 'adGroupId', 'targetingText', "targetingId"
]

SB_TARGETING_REPORT_COLUMNS = [
    'impressions', 'clicks', 'cost', 'purchases', "sales", "unitsSold",
    'keywordId', 'keywordText', 'date', 'campaignName', 'campaignId',
    'keywordBid', 'adGroupName', 'adGroupId', 'keywordType', 'matchType', ' targetingText', "targetingId"
]

TARGETING_REPORT_COLUMNS_MAPPING = {
    "spTargeting": SP_TARGETING_REPORT_COLUMNS,
    "sdTargeting": SD_TARGETING_REPORT_COLUMNS,
    "sbTargeting": SB_TARGETING_REPORT_COLUMNS,
}

class BiddingStrategy(Enum):
    MANUAL = "MANUAL"
    LEGACY_FOR_SALES = "LEGACY_FOR_SALES"
    RULE_BASED = "RULE_BASED"
    AUTO_FOR_SALES = "AUTO_FOR_SALES"


class TargetingType(Enum):
    AUTO = "AUTO"
    MANUAL = "MANUAL"

class MatchType(Enum):
    EXACT = "EXACT"
    PHRASE = "PHRASE"
    BROAD = "BROAD"

class State(Enum):
    ENABLED = "ENABLED"
    PAUSED = "PAUSED"
    PROPOSED = "PROPOSED"
    ARCHIVED = "ARCHIVED"
    USER_DELETED = "USER_DELETED"
    OTHER = "OTHER"