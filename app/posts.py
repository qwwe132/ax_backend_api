from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import Db
from .models import Post, User
from .schemas import PostRead, PostWrite
from .security import CurrentUser

router = APIRouter(prefix="/posts", tags=["게시글"])


def get_post_or_404(post_id: int, db: Session) -> Post:
    post = db.get(Post, post_id)
    if post is None:
        raise HTTPException(404, "게시글을 찾을 수 없습니다.")
    return post


def check_writer(post: Post, user: User) -> None:
    if post.author_id != user.id and user.role != "admin":
        raise HTTPException(403, "작성자 또는 관리자만 변경할 수 있습니다.")


@router.get("", response_model=list[PostRead])
def list_posts(
    db: Db,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[Post]:
    return list(db.scalars(select(Post).order_by(Post.id.desc()).offset(offset).limit(limit)))


@router.get("/{post_id}", response_model=PostRead)
def read_post(post_id: int, db: Db) -> Post:
    return get_post_or_404(post_id, db)


@router.post("", response_model=PostRead, status_code=status.HTTP_201_CREATED)
def create_post(body: PostWrite, user: CurrentUser, db: Db, response: Response) -> Post:
    post = Post(title=body.title, content=body.content, author_id=user.id)
    db.add(post)
    db.commit()
    db.refresh(post)
    response.headers["Location"] = f"/posts/{post.id}"
    return post


@router.put("/{post_id}", response_model=PostRead)
def update_post(post_id: int, body: PostWrite, user: CurrentUser, db: Db) -> Post:
    post = get_post_or_404(post_id, db)
    check_writer(post, user)
    post.title = body.title
    post.content = body.content
    db.commit()
    db.refresh(post)
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, user: CurrentUser, db: Db) -> Response:
    post = get_post_or_404(post_id, db)
    check_writer(post, user)
    db.delete(post)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
