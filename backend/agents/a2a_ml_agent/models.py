
from pydantic import BaseModel, Field
from typing import Optional, List

class MLRequest(BaseModel):
    model_type: str = Field(..., description="Type of model (churn, risk, fraud)")
    input_data: dict = Field(..., description="Data for prediction")

class MLResponse(BaseModel):
    prediction: Any
    confidence: float
    message: str
