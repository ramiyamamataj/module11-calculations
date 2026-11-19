from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app.models import User, Calculation  # noqa: F401
from app.schemas import UserCreate, UserRead, Token
from app.security import create_access_token

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="FastAPI Polymorphic Calculator API",
    version="1.1.0",
    lifespan=lifespan,
)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/users/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    try:
        return User.register(db, user_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.post("/users/login", response_model=Token)
def login_user(user_in: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_in.username).first()
    if not user or not user.check_password(user_in.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    token = create_access_token(data={"sub": str(user.id), "username": user.username})
    return Token(access_token=token)
