from enum import Enum


class AdsReportTypeId(Enum):
    SP_ADVERTISED_PRODUCT = "spAdvertisedProduct"
    SP_CAMPAIGN = "spCampaigns"
    SD_ADVERISED_PRODUCT = "sdAdvertisedProduct"
    SD_CAMPAING = "sdCampaigns"


class GroupBy(Enum):
    CAMPAIGN = "campaign"
    ADVERTISER = "advertiser"


class AdProduct(Enum):
    SPONSORED_PRODUCTS = "SPONSORED_PRODUCTS"
    SPONSORED_DISPLAY = "SPONSORED_DISPLAY"
    # SPONSORED_BRAND = "SPONSORED_BRAND"


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
SB_CAMPAING_REPORT_COLUMNS = ["sales", "impressions", "clicks", "cost", ]

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
    "unitsSoldClicks7d",
    "purchases7d",
]
SD_ADVERTISED_PRODUCT_COLUMNS = [
    "date", "impressions", "clicks", "cost", "sales", "promotedAsin", "purchases", "unitsSoldClicks"
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
