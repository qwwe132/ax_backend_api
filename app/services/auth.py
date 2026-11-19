from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models import User
from app.repositories import users
from app.schemas import Signup, Token
from app.security import create_token, dummy_hash, password_hasher, unauthorized

def signup(body: Signup, db: Session) -> User:
    user = User(username=body.username, password_hash=password_hasher.hash(body.password))
    try:
        users.add(db, user)
        db.commit()
    except IntegrityError as error:
        db.rollback()
        if getattr(error.orig, "sqlstate", None) == "23505":
            raise HTTPException(409, "이미 사용 중인 아이디입니다.") from None
        raise
    return user


def login(username: str, password: str, db: Session) -> Token:
    username = username.strip().lower()
    if len(username) > 32 or len(password) > 128:
        raise unauthorized("아이디 또는 비밀번호를 확인해 주세요.")

    user = users.get_by_username(db, username)
    valid = password_hasher.verify(password, user.password_hash if user else dummy_hash)
    if not valid or user is None:
        raise unauthorized("아이디 또는 비밀번호를 확인해 주세요.")
    return Token(access_token=create_token(user))
