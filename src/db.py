import os
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends
from sqlmodel import create_engine, SQLModel, Session

load_dotenv()

engine = create_engine(os.getenv("DB_URL"))


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
