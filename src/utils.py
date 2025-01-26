from datetime import datetime, timedelta, timezone
from typing import Literal

import jwt

from src.config import SettingsDep

ALGORITHM = "HS256"


def create_token(
    type: Literal["access", "refresh"], subject: str, settings: SettingsDep
) -> str:
    expire = (
        datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRY)
        if type == "access"
        else timedelta(days=settings.REFRESH_TOKEN_EXPIRY)
    )
    to_encode = {"exp": str(expire), "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt
