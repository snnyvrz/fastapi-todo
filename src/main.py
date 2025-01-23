from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.db import create_db_and_tables, SessionDep
from src.models import User, UserCreate

app = FastAPI()

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
async def read_root():
    return {"Hello": "Sina"}


@app.post("/signup/", response_model=User)
async def create_user(user: UserCreate, session: SessionDep):
    db_user = UserCreate.model_validate(user)
    if db_user.password != db_user.confirm_password:
        raise ValueError("Passwords do not match")
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
