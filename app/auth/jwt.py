from datetime import datetime, timedelta

from jose import jwt
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str

    class Config:
        env_file = ".env"


settings = Settings()

ALGORITHM = "HS256"


def create_token(email: str, role: str):
    data = {
        "email": email,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=1)
    }

    return jwt.encode(
        data,
        settings.SECRET_KEY,
        algorithm=ALGORITHM
    )