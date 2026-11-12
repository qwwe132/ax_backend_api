from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from .db import Db
from .models import User
from .schemas import Signup, Token, UserRead
from .security import CurrentUser, create_token, dummy_hash, password_hasher, unauthorized

router = APIRouter(prefix="/auth", tags=["인증"])


@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def signup(body: Signup, db: Db) -> User:
    user = User(username=body.username, password_hash=password_hasher.hash(body.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        if getattr(error.orig, "sqlstate", None) == "23505":
            raise HTTPException(409, "이미 사용 중인 아이디입니다.") from None
        raise
    return user


@router.post("/login", response_model=Token)
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: Db) -> Token:
    username = form.username.strip().lower()
    if len(username) > 32 or len(form.password) > 128:
        raise unauthorized("아이디 또는 비밀번호를 확인해 주세요.")

    user = db.scalar(select(User).where(User.username == username))
    valid = password_hasher.verify(form.password, user.password_hash if user else dummy_hash)
    if not valid or user is None:
        raise unauthorized("아이디 또는 비밀번호를 확인해 주세요.")
    return Token(access_token=create_token(user))


@router.get("/me", response_model=UserRead)
def me(user: CurrentUser) -> User:
    return user
