from datetime import datetime, timezone

from fastapi import Depends, FastAPI, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Message
from .schemas import MessageCreateRequest
from .security import TokenExpiredError, TokenSignatureInvalidError, decode_token

app = FastAPI(title="Message Service", version="1.0.1")
Base.metadata.create_all(bind=engine)
security = HTTPBearer(auto_error=False)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_, __):
    return Response(status_code=status.HTTP_400_BAD_REQUEST)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/messages", status_code=status.HTTP_201_CREATED)
def create_message(
    payload: MessageCreateRequest,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> Response:
    if not credentials or credentials.scheme.lower() != "bearer" or not credentials.credentials:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

    token = credentials.credentials.strip()

    try:
        claims = decode_token(token)
    except TokenSignatureInvalidError:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    except TokenExpiredError:
        return Response(status_code=status.HTTP_401_UNAUTHORIZED)

    user_id = claims.get("user_id")
    if not isinstance(user_id, int):
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

    message = Message(
        user_id=user_id,
        time=datetime.now(timezone.utc),
        message=payload.message,
    )
    db.add(message)
    db.commit()

    return Response(status_code=status.HTTP_201_CREATED)
