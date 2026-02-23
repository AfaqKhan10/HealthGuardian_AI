# app/schemas.py
from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime


class PatientCaseCreate(BaseModel):
    user_query: str  # user ka input (symptoms ki baat)


class PatientCaseOut(BaseModel):
    id: int
    user_id: int
    user_query: str
    extracted_symptoms: Optional[Dict] = None
    risk_level: Optional[str] = None
    escalation_flag: bool = False
    status: str
    final_response: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # SQLAlchemy se ORM mode enable