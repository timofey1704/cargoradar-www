"""Read-схемы постов (Post): их создают СТО, поставщики и водители."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from core.models.enums.post_creator_type import PostCreatorType
from core.schemas.search.page import PageRead


class PostRead(BaseModel):
    """Пост СТО, поставщика или водителя."""

    id: int
    creator_type: PostCreatorType
    client_id: int | None = None
    executor_id: int | None = None
    title: str
    request_text: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


PostPageRead = PageRead[PostRead]

