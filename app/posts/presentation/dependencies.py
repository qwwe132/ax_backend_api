from app.posts.application.service import PostService


def provider_post_service() -> PostService:
    raise NotImplementedError("PostService 의존성이 주입되지 않았습니다.")
