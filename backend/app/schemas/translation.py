from typing import Optional, Dict
from pydantic import BaseModel

class TranslationBase(BaseModel):
    key: str
    language_code: str
    value: str
    group: Optional[str] = "common"
    is_active: Optional[bool] = True

class TranslationCreate(TranslationBase):
    pass

class TranslationUpdate(BaseModel):
    value: Optional[str] = None
    is_active: Optional[bool] = None

class TranslationResponse(TranslationBase):
    id: int

    class Config:
        from_attributes = True

# Map for frontend: {"key": "value"}
TranslationMap = Dict[str, str]
