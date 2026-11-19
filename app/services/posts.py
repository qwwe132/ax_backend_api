from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models import Post, User
from app.repositories import posts
from app.schemas import PostWrite

def get_post_or_404(post_id: int, db: Session) -> Post:
    post = posts.get_by_id(db, post_id)
    if post is None:
        raise HTTPException(404, "게시글을 찾을 수 없습니다.")
    return post


def check_writer(post: Post, user: User) -> None:
    if post.author_id != user.id and user.role != "admin":
        raise HTTPException(403, "작성자 또는 관리자만 변경할 수 있습니다.")


def list_posts(
    db: Session,
    offset: int = 0,
    limit: int = 20,
) -> list[Post]:
    return posts.get_list(db, offset, limit)


def read_post(post_id: int, db: Session) -> Post:
    return get_post_or_404(post_id, db)


def create_post(body: PostWrite, user: User, db: Session) -> Post:
    post = Post(title=body.title, content=body.content, author_id=user.id)
    posts.add(db, post)
    db.commit()
    db.refresh(post)
    return post


def update_post(post_id: int, body: PostWrite, user: User, db: Session) -> Post:
    post = get_post_or_404(post_id, db)
    check_writer(post, user)
    post.title = body.title
    post.content = body.content
    db.commit()
    db.refresh(post)
    return post


def delete_post(post_id: int, user: User, db: Session) -> None:
    post = get_post_or_404(post_id, db)
    check_writer(post, user)
    posts.delete(db, post)
    db.commit()
