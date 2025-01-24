from fastapi import APIRouter, HTTPException
from passlib.context import CryptContext
from sqlmodel import select

from src.db import SessionDep
from src.models import User, UserCreate

api_router = APIRouter()


crypto_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@api_router.get("/")
async def read_root():
    return {"Hello": "Sina"}


@api_router.post("/signup/", response_model=User)
async def create_user(user: UserCreate, session: SessionDep):
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
    return db_user
