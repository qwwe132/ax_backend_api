from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import settings

database_url = make_url(settings.database_url.get_secret_value())
if database_url.drivername in ("postgresql", "postgres", "postgresql+asyncpg"):
    database_url = database_url.set(drivername="postgresql+psycopg")

engine = create_engine(database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session


Db = Annotated[Session, Depends(get_db)]
