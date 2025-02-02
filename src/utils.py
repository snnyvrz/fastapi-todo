from typing import Annotated, Literal
from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import select

from src.config import settings
from src.db import SessionDep
from src.models import TokenData, User, UserPublic

ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/signin")


def create_token(type: Literal["access", "refresh"], subject: str) -> str:
    expire = datetime.now(timezone.utc) + (
        timedelta(seconds=settings.ACCESS_TOKEN_EXPIRY)
        if type == "access"
        else timedelta(days=settings.REFRESH_TOKEN_EXPIRY)
    )
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


async def get_user(user_id: str, session: SessionDep) -> UserPublic | None:
    statement = select(User).where(User.id == UUID(user_id))
    user_obj = session.exec(statement).first()
    return user_obj


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except InvalidTokenError:
        raise credentials_exception
    user = await get_user(user_id=token_data.user_id, session=session)
    if user is None:
        raise credentials_exception
    return user
