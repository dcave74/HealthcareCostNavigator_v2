from pydantic import BaseModel
from typing import Optional, List

class ProviderBase(BaseModel):
    provider_id: int
    provider_name: str
    provider_city: str
    provider_state: str
    provider_zip_code: str
    provider_status: Optional[str] = "UNKNOWN"

class Provider(ProviderBase):
    class Config:
        from_attributes = True

class ProviderSearchResponse(BaseModel):
    provider_id: int
    provider_name: str
    average_covered_charges: Optional[int] = None

class QuestionRequest(BaseModel):
    question: str

class QuestionResponse(BaseModel):
    answer: str