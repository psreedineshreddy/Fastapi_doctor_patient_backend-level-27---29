from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PatientCreate(BaseModel):
    name: str
    age: int = Field(gt=0)
    phone: str
    doctor_id: int

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must contain exactly 10 digits")
        return value

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Deepak",
                "age": 28,
                "phone": "9876543210",
                "doctor_id": 1
            }
        }
    )


class PatientResponse(BaseModel):
    id: int
    name: str
    age: int
    phone: str
    doctor_id: int
    created_at: datetime
    updated_at: datetime
    created_by: str | None
    updated_by: str | None

    model_config = ConfigDict(from_attributes=True)


class PatientListResponse(BaseModel):
    total: int
    page: int
    limit: int
    data: list[PatientResponse]

    model_config = ConfigDict(from_attributes=True)
