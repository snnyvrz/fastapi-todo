import uuid

from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    username: str = Field(unique=True)


class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


class UserCreate(UserBase):
    password: str
    confirm_password: str
