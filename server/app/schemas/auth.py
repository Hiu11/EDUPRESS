from pydantic import BaseModel, ConfigDict, Field

from app.models.user import UserRole


class RegisterRequest(BaseModel):
    email: str = Field(pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$", max_length=255)
    password: str = Field(min_length=8, max_length=128)
    name: str = Field(min_length=1, max_length=120)


class LoginRequest(BaseModel):
    email: str = Field(pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$", max_length=255)
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int


class UserRead(BaseModel):
    id: int
    email: str
    name: str
    role: UserRole
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
