from sqlalchemy import select
from sqlalchemy.orm import Session
from app.posts.domain.post import Post
from .models import Post as PostModel

class SqlAlchemyPostRepository:
    def __init__(self, db: Session):
        self.db = db

    def to_domain(self, row: PostModel) -> Post:
        return Post(id=row.id, title=row.title, content=row.content, author_id=row.author_id,
                    created_at=row.created_at, updated_at=row.updated_at)

    def get_by_id(self, post_id: int) -> Post | None:
        row = self.db.get(PostModel, post_id)
        return self.to_domain(row) if row else None

    def get_list(self, offset: int, limit: int) -> list[Post]:
        rows = self.db.scalars(select(PostModel).order_by(PostModel.id.desc()).offset(offset).limit(limit))
        return [self.to_domain(row) for row in rows]

    def add(self, title: str, content: str, author_id: int) -> Post:
        row = PostModel(title=title, content=content, author_id=author_id)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self.to_domain(row)

    def update(self, post: Post) -> Post:
        row = self.db.get(PostModel, post.id)
        row.title = post.title
        row.content = post.content
        self.db.commit()
        self.db.refresh(row)
        return self.to_domain(row)

    def delete(self, post: Post) -> None:
        row = self.db.get(PostModel, post.id)
        self.db.delete(row)
        self.db.commit()
