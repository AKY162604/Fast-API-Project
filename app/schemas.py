from datetime import date
from pydantic import BaseModel

class APIResponse(BaseModel):
    id: int
    name: str
    status: str

class CrmResponse(APIResponse):
    email: str

    class Config:
        from_attributes = True


class MarketingResponse(APIResponse):
    budget: int
    start_date: str
    end_date: str

    class Config:
        from_attributes = True
