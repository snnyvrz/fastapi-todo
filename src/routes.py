from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext
from sqlmodel import select

from src.config import SettingsDep
from src.db import SessionDep
from src.models import User, UserCreate, UserLogin, Token
from src.utils import create_token

api_router = APIRouter()


crypto_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@api_router.get("/")
async def read_root():
    return {"Hello": "Sina"}


@api_router.post("/signup/", response_model=Token)
async def create_user(user: UserCreate, session: SessionDep, settings: SettingsDep):
    statement = select(User).where(User.username == user.username)
    user_object = session.exec(statement).first()

    if user_object:
        raise HTTPException(status_code=409, detail="Username already exists")

    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    del user.confirm_password

    db_user = User.model_validate(
        user, update={"hashed_password": crypto_context.hash(user.password)}
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    access_token = create_token(
        type="access", subject={"user_id": db_user.id}, settings=settings
    )
    refresh_token = create_token(
        type="refresh", subject={"user_id": db_user.id}, settings=settings
    )

    token = Token.model_validate(
        {"access_token": access_token, "refresh_token": refresh_token}
    )

    return token


@api_router.post("/signin/", response_model=Token)
async def login_user(user: UserLogin, session: SessionDep, settings: SettingsDep):
    statement = select(User).where(User.username == user.username)
    user_obj = session.exec(statement).first()

    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found")

    if not crypto_context.verify(user.password, user_obj.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect password")

    access_token = create_token(
        type="access", subject={"user_id": user_obj.id}, settings=settings
    )
    refresh_token = create_token(
        type="refresh", subject={"user_id": user_obj.id}, settings=settings
    )

    token = Token.model_validate(
        {"access_token": access_token, "refresh_token": refresh_token}
    )

    return token
