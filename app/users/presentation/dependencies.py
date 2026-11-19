from app.users.application.service import UserService


def provider_user_service() -> UserService:
    raise NotImplementedError("UserService 의존성이 주입되지 않았습니다.")
