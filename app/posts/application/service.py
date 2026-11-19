from app.posts.domain.post import Post
from app.posts.domain.repository import PostRepository
from app.shared.core.exceptions import AppException
from app.shared.domain.transaction import Transaction
from app.users.domain.user import User


class PostService:
    def __init__(self, repository: PostRepository, transaction: Transaction):
        self.repo = repository
        self.transaction = transaction

    def get_post(self, post_id: int) -> Post:
        post = self.repo.get_by_id(post_id)
        if post is None:
            raise AppException(404, "게시글을 찾을 수 없습니다.")
        return post

    def list_posts(self, offset: int, limit: int) -> list[Post]:
        return self.repo.get_list(offset, limit)

    def create_post(self, title: str, content: str, user: User) -> Post:
        try:
            post = self.repo.add(title, content, user.id)
            self.transaction.commit()
            return post
        except Exception:
            self.transaction.rollback()
            raise

    def update_post(self, post_id: int, title: str, content: str, user: User) -> Post:
        try:
            post = self.get_post(post_id)
            post.update_info(title, content, user)
            updated = self.repo.update(post)
            self.transaction.commit()
            return updated
        except Exception:
            self.transaction.rollback()
            raise

    def delete_post(self, post_id: int, user: User) -> None:
        try:
            post = self.get_post(post_id)
            post.authorize_writer(user)
            self.repo.delete(post)
            self.transaction.commit()
        except Exception:
            self.transaction.rollback()
            raise
