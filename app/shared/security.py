from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

from .config import settings
from app.users.presentation.dependencies import Repository
from app.users.domain.user import User

password_hasher = PasswordHash.recommended()
dummy_hash = password_hasher.hash("unused-password-for-unknown-account")
bearer = OAuth2PasswordBearer(tokenUrl="auth/login")
issuer = "board-api"


def create_token(user: User) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {"sub": str(user.id), "iss": issuer, "iat": now,
         "exp": now + timedelta(minutes=settings.token_minutes)},
        settings.jwt_secret.get_secret_value(),
        algorithm="HS256",
    )


def unauthorized(message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=message,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(token: Annotated[str, Depends(bearer)], repository: Repository) -> User:
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
        raise unauthorized("토큰이 유효하지 않거나 만료되었습니다.") from None

    user = repository.get_by_id(user_id)
    if user is None:
        raise unauthorized("사용자를 확인할 수 없습니다.")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
