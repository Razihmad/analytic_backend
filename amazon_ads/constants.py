from enum import Enum


class AdsReportTypeId(Enum):
    SP_ADVERTISED_PRODUCT = "spAdvertisedProduct"
    SP_CAMPAIGN = "spCampaigns"


class GroupBy(Enum):
    CAMPAIGN = "campaign"
    ADVERTISER = "advertiser"


class AdProduct(Enum):
    SPONSORED_PRODUCTS = "SPONSORED_PRODUCTS"
    SPONSORED_DISPLAY = "SPONSORED_DISPLAY"
    SPONSORED_BRAND = "SPONSORED_BRAND"


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
    "date", "costPerClick", "clickThroughRate", "campaignName",
    "impressions", "clicks", "cost", "spend", "campaignBiddingStrategy",
    "campaignStatus", "campaignId",
]
SP_CAMPAIGN_REPORT_COLUMNS = CAMPAIGN_REPORT_COMMON_COLUMNS + [
    "sales14d", "unitsSoldClicks14d", "purchases14d"
]
SD_CAMPAIGN_REPORT_COLUMNS = CAMPAIGN_REPORT_COMMON_COLUMNS + ["sales", "unitsSoldClicks", "purchases"]
SB_CAMPAING_REPORT_COLUMNS = SD_CAMPAIGN_REPORT_COLUMNS

CAMPAIGN_COLUMNS = {
    "SPONSORED_PRODUCTS": SP_CAMPAIGN_REPORT_COLUMNS,
    "SPONSORED_BRAND": SB_CAMPAING_REPORT_COLUMNS,
    "SPONSORED_DISPLAY": SD_CAMPAIGN_REPORT_COLUMNS,
}
