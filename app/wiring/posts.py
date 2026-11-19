from fastapi import FastAPI

from app.posts.application.service import PostService
from app.posts.infrastructure.repositories import SqlAlchemyPostRepository
from app.posts.presentation.dependencies import provider_post_service
from app.shared.core.database import Db
from app.shared.infrastructure.transaction import SqlAlchemyTransaction


def create_post_service(db: Db) -> PostService:
    return PostService(SqlAlchemyPostRepository(db), SqlAlchemyTransaction(db))


def wire_dependencies(app: FastAPI) -> None:
    app.dependency_overrides[provider_post_service] = create_post_service
