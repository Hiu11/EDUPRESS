from enum import Enum

from sqlalchemy import Boolean, Float, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CourseAccessType(str, Enum):
    free = "free"
    paid = "paid"


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    slug: Mapped[str | None] = mapped_column(String(80), unique=True, index=True, nullable=True)
    title: Mapped[str] = mapped_column(String(180), index=True)
    author: Mapped[str] = mapped_column(String(120))
    category: Mapped[str] = mapped_column(String(80), index=True)
    description: Mapped[str] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    level: Mapped[str | None] = mapped_column(String(40), nullable=True)
    lessons: Mapped[int | None] = mapped_column(Integer, default=0, nullable=True)
    duration: Mapped[str | None] = mapped_column(String(80), nullable=True)
    rating: Mapped[float | None] = mapped_column(Float, default=0, nullable=True)
    students: Mapped[int | None] = mapped_column(Integer, default=0, nullable=True)
    progress: Mapped[int | None] = mapped_column(Integer, default=0, nullable=True)
    tag: Mapped[str | None] = mapped_column(String(80), nullable=True)
    access_type: Mapped[str] = mapped_column(String(20), default=CourseAccessType.free.value)
    price_cents: Mapped[int] = mapped_column(Integer, default=0)
    currency: Mapped[str] = mapped_column(String(3), default="VND")
    manual_enrollment_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    outcomes: Mapped[list[str] | None] = mapped_column(JSON, default=list, nullable=True)
    syllabus: Mapped[list[str] | None] = mapped_column(JSON, default=list, nullable=True)
    resources: Mapped[list[str] | None] = mapped_column(JSON, default=list, nullable=True)
