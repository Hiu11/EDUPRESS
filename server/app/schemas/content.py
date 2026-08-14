from typing import Any

from pydantic import BaseModel, ConfigDict


class ContentItemCreate(BaseModel):
    slug: str
    title: str
    payload: dict[str, Any]


class ContentItemUpdate(BaseModel):
    slug: str | None = None
    title: str | None = None
    payload: dict[str, Any] | None = None


class ContentItemRead(ContentItemCreate):
    id: int
    kind: str

    model_config = ConfigDict(from_attributes=True)
