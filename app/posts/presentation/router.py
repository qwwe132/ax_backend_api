from typing import Annotated

from fastapi import APIRouter, Query, Response, status
from app.posts.application import service as posts

from app.posts.presentation.dependencies import Repository
from app.posts.domain.post import Post
from app.posts.presentation.schemas import PostRead, PostWrite
from app.shared.security import CurrentUser

router = APIRouter(prefix="/posts", tags=["게시글"])


@router.get("", response_model=list[PostRead])
def list_posts(
    repository: Repository,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[Post]:
    return posts.list_posts(repository, offset, limit)


@router.get("/{post_id}", response_model=PostRead)
def read_post(post_id: int, repository: Repository) -> Post:
    return posts.read_post(post_id, repository)


@router.post("", response_model=PostRead, status_code=status.HTTP_201_CREATED)
def create_post(body: PostWrite, user: CurrentUser, repository: Repository, response: Response) -> Post:
    post = posts.create_post(body, user, repository)
    response.headers["Location"] = f"/posts/{post.id}"
    return post


@router.put("/{post_id}", response_model=PostRead)
def update_post(post_id: int, body: PostWrite, user: CurrentUser, repository: Repository) -> Post:
    return posts.update_post(post_id, body, user, repository)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, user: CurrentUser, repository: Repository) -> Response:
    posts.delete_post(post_id, user, repository)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
