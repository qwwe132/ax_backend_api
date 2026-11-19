from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status

from app.posts.application.service import PostService
from app.posts.domain.post import Post
from app.shared.presentation.auth import CurrentUser
from .dependencies import provider_post_service
from .schemas import PostRead, PostWrite

router = APIRouter(prefix="/posts", tags=["게시글"])
Service = Annotated[PostService, Depends(provider_post_service)]


@router.get("", response_model=list[PostRead])
def list_posts(
    service: Service,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[Post]:
    return service.list_posts(offset, limit)


@router.get("/{post_id}", response_model=PostRead)
def read_post(post_id: int, service: Service) -> Post:
    return service.get_post(post_id)


@router.post("", response_model=PostRead, status_code=status.HTTP_201_CREATED)
def create_post(body: PostWrite, user: CurrentUser, service: Service, response: Response) -> Post:
    post = service.create_post(body.title, body.content, user)
    response.headers["Location"] = f"/posts/{post.id}"
    return post


@router.put("/{post_id}", response_model=PostRead)
def update_post(post_id: int, body: PostWrite, user: CurrentUser, service: Service) -> Post:
    return service.update_post(post_id, body.title, body.content, user)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, user: CurrentUser, service: Service) -> Response:
    service.delete_post(post_id, user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
