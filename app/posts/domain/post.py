from dataclasses import dataclass
from datetime import datetime
from app.users.domain.user import User
from app.shared.core.exceptions import AppException

@dataclass
class Post:
    id: int
    title: str
    content: str
    author_id: int
    created_at: datetime
    updated_at: datetime

    def authorize_writer(self, user: User) -> None:
        if self.author_id != user.id and user.role != "admin":
            raise AppException(403, "작성자 또는 관리자만 변경할 수 있습니다.")

    def update_info(self, title: str, content: str, user: User) -> None:
        self.authorize_writer(user)
        self.title = title
        self.content = content
