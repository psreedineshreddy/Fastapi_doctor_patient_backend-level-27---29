from pydantic import BaseModel, EmailStr, ConfigDict


class DoctorCreate(BaseModel):
    name: str
    specialization: str
    email: EmailStr

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Dinesh Reddy",
                "specialization": "Cardiology",
                "email": "dineshreddy@example.com"
            }
        }
    )


class DoctorUpdate(BaseModel):
    name: str
    specialization: str
    email: EmailStr

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Updated Doctor",
                "specialization": "Neurology",
                "email": "doctor@example.com"
            }
        }
    )


class DoctorResponse(BaseModel):
    id: int
    name: str
    specialization: str
    email: EmailStr
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class DoctorListResponse(BaseModel):
    total: int
    page: int
    limit: int
    data: list[DoctorResponse]

    model_config = ConfigDict(from_attributes=True)