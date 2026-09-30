from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from app.auth.jwt import settings, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])

        email = payload.get("email")
        role = payload.get("role")

        if not email or not role:
            raise HTTPException(status_code=401, detail="Invalid token")

        return {
            "email": email,
            "role": role
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")