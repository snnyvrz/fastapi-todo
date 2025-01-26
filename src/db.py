from typing import Annotated

from fastapi import Depends
from sqlmodel import create_engine, SQLModel, Session

from src.config import Settings, get_settings


def get_engine(settings: Settings = get_settings()):
    return create_engine(settings.DATABASE_URL)


engine = get_engine()


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
