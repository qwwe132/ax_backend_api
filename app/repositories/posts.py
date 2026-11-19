from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Post


def get_by_id(db: Session, post_id: int) -> Post | None:
    return db.get(Post, post_id)


def get_list(db: Session, offset: int, limit: int) -> list[Post]:
    return list(db.scalars(select(Post).order_by(Post.id.desc()).offset(offset).limit(limit)))


def add(db: Session, post: Post) -> None:
    db.add(post)
    db.flush()


def delete(db: Session, post: Post) -> None:
    db.delete(post)
