import os

import jwt
from jwt import ExpiredSignatureError, InvalidSignatureError, InvalidTokenError

JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-change-me")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


class TokenSignatureInvalidError(ValueError):
    pass


class TokenExpiredError(ValueError):
    pass



def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except ExpiredSignatureError as exc:
        raise TokenExpiredError("Token expired") from exc
    except InvalidSignatureError as exc:
        raise TokenSignatureInvalidError("Invalid token signature") from exc
    except InvalidTokenError as exc:
        raise TokenSignatureInvalidError("Invalid token") from exc
