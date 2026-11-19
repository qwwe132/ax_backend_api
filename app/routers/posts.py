from typing import Annotated

from fastapi import APIRouter, Query, Response, status
from app.services import posts

from app.db import Db
from app.models import Post
from app.schemas import PostRead, PostWrite
from app.security import CurrentUser

router = APIRouter(prefix="/posts", tags=["게시글"])


@router.get("", response_model=list[PostRead])
def list_posts(
    db: Db,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[Post]:
    return posts.list_posts(db, offset, limit)


@router.get("/{post_id}", response_model=PostRead)
def read_post(post_id: int, db: Db) -> Post:
    return posts.read_post(post_id, db)


@router.post("", response_model=PostRead, status_code=status.HTTP_201_CREATED)
def create_post(body: PostWrite, user: CurrentUser, db: Db, response: Response) -> Post:
    post = posts.create_post(body, user, db)
    response.headers["Location"] = f"/posts/{post.id}"
    return post


@router.put("/{post_id}", response_model=PostRead)
def update_post(post_id: int, body: PostWrite, user: CurrentUser, db: Db) -> Post:
    return posts.update_post(post_id, body, user, db)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, user: CurrentUser, db: Db) -> Response:
    posts.delete_post(post_id, user, db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
