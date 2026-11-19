from fastapi import HTTPException
from app.users.domain.user import User
from app.users.domain.repository import UserRepository, UsernameTakenError
from app.users.presentation.schemas import Signup, Token
from app.shared.security import create_token, dummy_hash, password_hasher, unauthorized

def signup(body: Signup, repository: UserRepository) -> User:
    try:
        return repository.add(body.username, password_hasher.hash(body.password))
    except UsernameTakenError:
        raise HTTPException(409, "이미 사용 중인 아이디입니다.") from None



def login(username: str, password: str, repository: UserRepository) -> Token:
    username = username.strip().lower()
    if len(username) > 32 or len(password) > 128:
        raise unauthorized("아이디 또는 비밀번호를 확인해 주세요.")

    user = repository.get_by_username(username)
    valid = password_hasher.verify(password, user.password_hash if user else dummy_hash)
    if not valid or user is None:
        raise unauthorized("아이디 또는 비밀번호를 확인해 주세요.")
    return Token(access_token=create_token(user))
