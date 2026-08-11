from pydantic import BaseModel, ConfigDict, Field


class CourseBase(BaseModel):
    slug: str | None = None
    title: str
    author: str
    category: str
    description: str
    image_url: str | None = None
    level: str | None = None
    lessons: int = 0
    duration: str | None = None
    rating: float = 0
    students: int = 0
    progress: int = 0
    tag: str | None = None
    outcomes: list[str] = Field(default_factory=list)
    syllabus: list[str] = Field(default_factory=list)
    resources: list[str] = Field(default_factory=list)


class CourseCreate(CourseBase):
    pass


class CourseRead(CourseBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
