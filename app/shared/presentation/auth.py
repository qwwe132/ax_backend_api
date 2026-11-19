from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.shared.core.security import decode_token
from app.users.application.service import UserService
from app.users.domain.user import User
from app.users.presentation.dependencies import provider_user_service

bearer = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(
    token: Annotated[str, Depends(bearer)],
    service: Annotated[UserService, Depends(provider_user_service)],
) -> User:
    return service.get_user(decode_token(token))


CurrentUser = Annotated[User, Depends(get_current_user)]
