from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from app.services import auth

from app.db import Db
from app.models import User
from app.schemas import Signup, Token, UserRead
from app.security import CurrentUser

router = APIRouter(prefix="/auth", tags=["인증"])


@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def signup(body: Signup, db: Db) -> User:
    return auth.signup(body, db)


@router.post("/login", response_model=Token)
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: Db) -> Token:
    return auth.login(form.username, form.password, db)


@router.get("/me", response_model=UserRead)
def me(user: CurrentUser) -> User:
    return user
