from enum import Enum

class NegativeKeywordEndpoint(Enum):
    LIST = "/sp/negativeKeywords/list"
    CREATE = "/sp/negativeKeywords"
    UPDATE = "/sp/negativeKeywords"
    DELETE = "/sp/negativeKeywords/delete"

class KeywordEndpoint(Enum):
    CREATE = "/sp/keywords"
