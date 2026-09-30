from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class BillingCreate(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_id: Optional[int] = None
    consultation_fee: Decimal = Field(gt=0)
    additional_charges: Decimal = Field(default=0, ge=0)
    payment_status: str = "pending"
    payment_mode: Optional[str] = None


class BillingUpdate(BaseModel):
    consultation_fee: Optional[Decimal] = Field(default=None, gt=0)
    additional_charges: Optional[Decimal] = Field(default=None, ge=0)
    payment_status: Optional[str] = None
    payment_mode: Optional[str] = None


class BillingResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    appointment_id: Optional[int]
    consultation_fee: Decimal
    additional_charges: Decimal
    total_amount: Decimal
    payment_status: str
    payment_mode: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True