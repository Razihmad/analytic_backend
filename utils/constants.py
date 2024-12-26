from enum import Enum


class BaseEndpoint(Enum):
    US = "https://sellercentral.amazon.com"
    Canada = "https://sellercentral.amazon.ca"
    Mexico = "https://sellercentral.amazon.com.mx"
    Brazil = "https://sellercentral.amazon.com.br"
