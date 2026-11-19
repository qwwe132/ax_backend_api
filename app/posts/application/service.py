from fastapi import HTTPException
from app.posts.domain.post import Post
from app.users.domain.user import User
from app.posts.domain.repository import PostRepository
from app.posts.presentation.schemas import PostWrite

def get_post_or_404(post_id: int, repository: PostRepository) -> Post:
    post = repository.get_by_id(post_id)
    if post is None:
        raise HTTPException(404, "게시글을 찾을 수 없습니다.")
    return post


def check_writer(post: Post, user: User) -> None:
    if post.author_id != user.id and user.role != "admin":
        raise HTTPException(403, "작성자 또는 관리자만 변경할 수 있습니다.")


def list_posts(
    repository: PostRepository,
    offset: int = 0,
    limit: int = 20,
) -> list[Post]:
    return repository.get_list(offset, limit)


def read_post(post_id: int, repository: PostRepository) -> Post:
    return get_post_or_404(post_id, repository)


def create_post(body: PostWrite, user: User, repository: PostRepository) -> Post:
    return repository.add(body.title, body.content, user.id)



def update_post(post_id: int, body: PostWrite, user: User, repository: PostRepository) -> Post:
    post = get_post_or_404(post_id, repository)
    check_writer(post, user)
    post.title = body.title
    post.content = body.content
    return repository.update(post)


def delete_post(post_id: int, user: User, repository: PostRepository) -> None:
    post = get_post_or_404(post_id, repository)
    check_writer(post, user)
    repository.delete(post)
