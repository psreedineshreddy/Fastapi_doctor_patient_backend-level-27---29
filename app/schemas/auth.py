from pydantic import BaseModel, ConfigDict, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    role: str = "doctor"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "doctor@example.com",
                "password": "Doctor@123",
                "role": "doctor"
            }
        }
    )


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "doctor@example.com",
                "password": "Doctor@123"
            }
        }
    )