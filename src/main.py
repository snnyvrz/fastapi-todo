from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from passlib.context import CryptContext

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


crypto_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@app.get("/")
async def read_root():
    return {"Hello": "Sina"}


@app.post("/signup/", response_model=User)
async def create_user(user: UserCreate, session: SessionDep):
    if user.password != user.confirm_password:
        raise ValueError("Passwords do not match")

    del user.confirm_password

    db_user = User.model_validate(
        user, update={"hashed_password": crypto_context.hash(user.password)}
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
