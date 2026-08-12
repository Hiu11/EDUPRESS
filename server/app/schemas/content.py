from typing import Any

from pydantic import BaseModel, ConfigDict


class ContentItemCreate(BaseModel):
    slug: str
    title: str
    payload: dict[str, Any]


class ContentItemRead(ContentItemCreate):
    id: int
    kind: str

    model_config = ConfigDict(from_attributes=True)
