from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import User
from .schemas import LoginRequest, RegisterRequest, TokenResponse
from .security import (
    WeakPasswordError,
    create_access_token,
    hash_password,
    validate_password_strength,
    verify_password,
)

app = FastAPI(title="Auth Service", version="1.0.0")
Base.metadata.create_all(bind=engine)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, __):
    return Response(status_code=status.HTTP_400_BAD_REQUEST)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> Response:
    try:
        validate_password_strength(payload.password)
    except WeakPasswordError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    existing_user = db.execute(select(User).where(User.email == payload.email)).scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

    user = User(email=payload.email, password=hash_password(payload.password))
    db.add(user)
    db.commit()
    return Response(status_code=status.HTTP_201_CREATED)


@app.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.execute(select(User).where(User.email == payload.email)).scalar_one_or_none()
    if not user:
        return Response(status_code=status.HTTP_401_UNAUTHORIZED)

    if not verify_password(payload.password, user.password):
        return Response(status_code=status.HTTP_401_UNAUTHORIZED)

    token, expires_at = create_access_token(user.id)
    return TokenResponse(token=token, expires_at=expires_at)
