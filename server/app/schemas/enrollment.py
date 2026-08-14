from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EnrollmentRequest(BaseModel):
    course_id: int
    note: str | None = Field(default=None, max_length=500)


class EnrollmentRead(BaseModel):
    id: int
    user_id: int
    course_id: int
    status: str
    payment_provider: str | None = None
    payment_reference: str | None = None
    note: str | None = None
    requested_at: datetime
    approved_at: datetime | None = None
    expires_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class EnrollmentAccessRead(BaseModel):
    course_id: int
    access_type: str
    is_enrolled: bool
    access_state: str
    enrollment: EnrollmentRead | None = None
