from app.shared.core.exceptions import AppException
from app.shared.domain.transaction import Transaction
from app.shared.core.security import create_token, dummy_hash, password_hasher
from app.users.domain.repository import UserRepository, UsernameTakenError
from app.users.domain.user import User


class UserService:
    def __init__(self, repository: UserRepository, transaction: Transaction):
        self.repo = repository
        self.transaction = transaction

    def signup(self, username: str, password: str) -> User:
        try:
            user = self.repo.add(username, password_hasher.hash(password))
            self.transaction.commit()
            return user
        except UsernameTakenError:
            self.transaction.rollback()
            raise AppException(409, "이미 사용 중인 아이디입니다.") from None
        except Exception:
            self.transaction.rollback()
            raise

    def login(self, username: str, password: str) -> str:
        username = username.strip().lower()
        if len(username) > 32 or len(password) > 128:
            raise AppException(401, "아이디 또는 비밀번호를 확인해 주세요.")

        user = self.repo.get_by_username(username)
        valid = password_hasher.verify(password, user.password_hash if user else dummy_hash)
        if not valid or user is None:
            raise AppException(401, "아이디 또는 비밀번호를 확인해 주세요.")
        return create_token(user)

    def get_user(self, user_id: int) -> User:
        user = self.repo.get_by_id(user_id)
        if user is None:
            raise AppException(401, "사용자를 확인할 수 없습니다.")
        return user
