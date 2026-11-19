from typing import Annotated
from fastapi import Depends
from app.db import Db
from app.users.domain.repository import UserRepository
from app.users.infrastructure.repositories import SqlAlchemyUserRepository

def get_repository(db: Db) -> UserRepository:
    return SqlAlchemyUserRepository(db)

Repository = Annotated[UserRepository, Depends(get_repository)]
