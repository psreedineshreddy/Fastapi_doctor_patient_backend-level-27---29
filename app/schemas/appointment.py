from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class AppointmentCreate(BaseModel):
    doctor_id: int
    patient_id: int
    appointment_date: datetime
    status: Literal["scheduled", "completed", "cancelled"] = "scheduled"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "doctor_id": 1,
                "patient_id": 1,
                "appointment_date": "2026-09-30T10:00:00",
                "status": "scheduled"
            }
        }
    )


class AppointmentResponse(BaseModel):
    id: int
    doctor_id: int
    patient_id: int
    appointment_date: datetime
    status: str
    created_at: datetime
    updated_at: datetime
    created_by: str | None
    updated_by: str | None

    model_config = ConfigDict(from_attributes=True)