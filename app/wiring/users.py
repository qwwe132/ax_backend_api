from fastapi import FastAPI

from app.shared.core.database import Db
from app.shared.infrastructure.transaction import SqlAlchemyTransaction
from app.users.application.service import UserService
from app.users.infrastructure.repositories import SqlAlchemyUserRepository
from app.users.presentation.dependencies import provider_user_service


def create_user_service(db: Db) -> UserService:
    return UserService(SqlAlchemyUserRepository(db), SqlAlchemyTransaction(db))


def wire_dependencies(app: FastAPI) -> None:
    app.dependency_overrides[provider_user_service] = create_user_service
