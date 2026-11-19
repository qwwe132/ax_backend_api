from typing import Annotated
from fastapi import Depends
from app.db import Db
from app.posts.domain.repository import PostRepository
from app.posts.infrastructure.repositories import SqlAlchemyPostRepository

def get_repository(db: Db) -> PostRepository:
    return SqlAlchemyPostRepository(db)

Repository = Annotated[PostRepository, Depends(get_repository)]
