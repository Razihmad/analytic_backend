from pydantic import BaseModel


class FetchData(BaseModel):
    start_date: str
    end_date: str
    amazon_seller_id: str
