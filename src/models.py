import uuid

from sqlmodel import Field, SQLModel
from pydantic import BaseModel


class UserBase(SQLModel):
    username: str = Field(unique=True, index=True)


class UserPublic(UserBase):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


class User(UserPublic, table=True):
    hashed_password: str


class TokenData(BaseModel):
    user_id: str | None = None
