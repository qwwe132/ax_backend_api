from typing import Protocol
from .user import User

class UserRepository(Protocol):
    def get_by_id(self, user_id: int) -> User | None: ...
    def get_by_username(self, username: str) -> User | None: ...
    def add(self, username: str, password_hash: str) -> User: ...


class UsernameTakenError(Exception):
    pass
