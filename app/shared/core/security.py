from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from .config import settings
from .exceptions import AppException
from app.users.domain.user import User

password_hasher = PasswordHash.recommended()
dummy_hash = password_hasher.hash("unused-password-for-unknown-account")
issuer = "board-api"

def create_token(user: User) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {"sub": str(user.id), "iss": issuer, "iat": now,
         "exp": now + timedelta(minutes=settings.token_minutes)},
        settings.jwt_secret.get_secret_value(),
        algorithm="HS256",
    )



def decode_token(token: str) -> int:
    try:
        claims = jwt.decode(
            token,
            settings.jwt_secret.get_secret_value(),
            algorithms=["HS256"],
            issuer=issuer,
            options={"require": ["sub", "exp", "iat"]},
        )
        user_id = int(claims["sub"])
    except (jwt.InvalidTokenError, ValueError):
        raise AppException(401, "토큰이 유효하지 않거나 만료되었습니다.") from None

    return user_id
