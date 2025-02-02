from typing import Annotated, Dict

import jwt
from fastapi import APIRouter, HTTPException, Cookie, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlmodel import select

from src.config import settings
from src.db import SessionDep
from src.models import User, UserPublic
from src.utils import create_token, ALGORITHM, get_current_user

api_router = APIRouter(prefix="/auth")


crypto_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@api_router.get("/me/", response_model=UserPublic)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user


@api_router.post("/signup/")
async def create_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
    response: Response,
):
    statement = select(User).where(User.username == form_data.username)
    user_object = session.exec(statement).first()

    if user_object:
        raise HTTPException(status_code=409, detail="Username already exists")

    db_user = User(
        username=form_data.username,
        hashed_password=crypto_context.hash(form_data.password),
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    access_token = create_token(type="access", subject=db_user.id)

    response.headers["Authorization"] = f"Bearer {access_token}"

    refresh_token = create_token(type="refresh", subject=db_user.id)

    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)

    return {"access_token": access_token}


@api_router.post("/signin/")
async def login_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
    response: Response,
):
    statement = select(User).where(User.username == form_data.username)
    user_obj = session.exec(statement).first()

    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")

    if not crypto_context.verify(form_data.password, user_obj.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect password")

    access_token = create_token(type="access", subject=user_obj.id)

    response.headers["Authorization"] = f"Bearer {access_token}"

    refresh_token = create_token(type="refresh", subject=user_obj.id)

    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)

    return {"access_token": access_token}


@api_router.get("/refresh/")
async def refresh(
    refresh_token: Annotated[str | None, Cookie()], response: Response
) -> Dict[str, str]:
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token not found")

    try:
        decoded = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=ALGORITHM)
        new_access_token = create_token(type="access", subject=decoded["sub"])
        response.headers["Authorization"] = f"Bearer {new_access_token}"
        return {"access_token": new_access_token}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
