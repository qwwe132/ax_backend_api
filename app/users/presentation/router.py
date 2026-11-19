from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from app.users.application import service as auth

from app.users.presentation.dependencies import Repository
from app.users.domain.user import User
from app.users.presentation.schemas import Signup, Token, UserRead
from app.shared.security import CurrentUser

router = APIRouter(prefix="/auth", tags=["인증"])


@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def signup(body: Signup, repository: Repository) -> User:
    return auth.signup(body, repository)


@router.post("/login", response_model=Token)
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], repository: Repository) -> Token:
    return auth.login(form.username, form.password, repository)


@router.get("/me", response_model=UserRead)
def me(user: CurrentUser) -> User:
    return user
