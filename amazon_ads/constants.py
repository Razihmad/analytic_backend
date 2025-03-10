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
