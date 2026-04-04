import os
import re
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-change-me")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))


class WeakPasswordError(ValueError):
    pass



def validate_password_strength(password: str) -> None:
    if len(password) < 8:
        raise WeakPasswordError("Password must be at least 8 characters long")
    if not re.search(r"[A-Z]", password):
        raise WeakPasswordError("Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", password):
        raise WeakPasswordError("Password must contain at least one lowercase letter")
    if not re.search(r"\d", password):
        raise WeakPasswordError("Password must contain at least one digit")
    if not re.search(r"[^A-Za-z0-9]", password):
        raise WeakPasswordError("Password must contain at least one special character")



def hash_password(password: str) -> str:
    return pwd_context.hash(password)



def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)



def create_access_token(user_id: int) -> tuple[str, int]:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {
        "user_id": user_id,
        "exp": expires_at,
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token, int(expires_at.timestamp())
