from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date, datetime
from uuid import UUID
from decimal import Decimal

class TelematicsDataBase(BaseModel):
    device_id: str
    trip_date: date
    distance_km: Decimal
    avg_speed: Decimal
    max_speed: Decimal
    harsh_braking_count: int = 0
    harsh_acceleration_count: int = 0
    night_driving_km: Optional[Decimal] = 0

class TelematicsDataCreate(TelematicsDataBase):
    policy_id: UUID

class TelematicsData(TelematicsDataBase):
    id: UUID
    policy_id: UUID
    safety_score: Optional[Decimal]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
