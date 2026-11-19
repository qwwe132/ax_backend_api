from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.shared.presentation.auth import CurrentUser
from app.users.application.service import UserService
from app.users.domain.user import User
from .dependencies import provider_user_service
from .schemas import Signup, Token, UserRead

router = APIRouter(prefix="/auth", tags=["인증"])
Service = Annotated[UserService, Depends(provider_user_service)]


@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def signup(body: Signup, service: Service) -> User:
    return service.signup(body.username, body.password)


@router.post("/login", response_model=Token)
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], service: Service) -> Token:
    return Token(access_token=service.login(form.username, form.password))


@router.get("/me", response_model=UserRead)
def me(user: CurrentUser) -> User:
    return user
