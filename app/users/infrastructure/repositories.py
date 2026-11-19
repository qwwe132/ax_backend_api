from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.users.domain.user import User
from .models import User as UserModel

from app.users.domain.repository import UsernameTakenError

class SqlAlchemyUserRepository:
    def __init__(self, db: Session):
        self.db = db

    def to_domain(self, row: UserModel) -> User:
        return User(id=row.id, username=row.username, password_hash=row.password_hash, role=row.role)

    def get_by_id(self, user_id: int) -> User | None:
        row = self.db.get(UserModel, user_id)
        return self.to_domain(row) if row else None

    def get_by_username(self, username: str) -> User | None:
        row = self.db.scalar(select(UserModel).where(UserModel.username == username))
        return self.to_domain(row) if row else None

    def add(self, username: str, password_hash: str) -> User:
        row = UserModel(username=username, password_hash=password_hash)
        self.db.add(row)
        try:
            self.db.commit()
        except IntegrityError as error:
            self.db.rollback()
            if getattr(error.orig, "sqlstate", None) == "23505":
                raise UsernameTakenError from None
            raise
        self.db.refresh(row)
        return self.to_domain(row)
