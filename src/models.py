import uuid

from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    username: str = Field(unique=True, index=True)


class UserLogin(UserBase):
    password: str


class UserCreate(UserLogin):
    confirm_password: str


class UserPublic(UserBase):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


class User(UserPublic, table=True):
    hashed_password: str
