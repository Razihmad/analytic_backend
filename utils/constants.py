from enum import Enum


class BaseEndpoint(Enum):
    US = "https://sellercentral.amazon.com"
    CANADA = "https://sellercentral.amazon.ca"
    MEXICO = "https://sellercentral.amazon.com.mx"
    BRAZIL = "https://sellercentral.amazon.com.br"
    IRELAND = "https://sellercentral.amazon.ie"
    SPAIN = "https://sellercentral-europe.amazon.com"
    UK = "https://sellercentral-europe.amazon.com"
    FRANCE = "https://sellercentral-europe.amazon.com"
    BELGIUM = "https://sellercentral.amazon.com.be"
    NETHERLANDS = "https://sellercentral.amazon.nl"
    GERMANY = "https://sellercentral-europe.amazon.com"
    ITALY = "https://sellercentral-europe.amazon.com"
    SWEDEN = "https://sellercentral.amazon.se"
    POLAND = "https://sellercentral.amazon.pl"
    EGYPT = "https://sellercentral.amazon.eg"
    TURKEY = "https://sellercentral.amazon.com.tr"
    INDIA = "https://sellercentral.amazon.in"
    SSINGAPORE = "https://sellercentral.amazon.sg"
    AUSTRAILIA = "https://sellercentral.amazon.com.au"
    JAPAN = "https://sellercentral.amazon.co.jp"


AMAZON_ADS_LOGIN_BASE_URL = {
    "eu-west-1": "https://eu.account.amazon.com/ap/oa",
    "us-east-1": "https://www.amazon.com/ap/oa",
    "us-west-2": "https://apac.account.amazon.com/ap/oa",
}
