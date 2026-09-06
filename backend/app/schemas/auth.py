from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UserRegister(BaseModel):
    user_name: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=8, max_length=128)
    age: int | None = None
    gender: str | None = Field(default=None, max_length=20)

    model_config = ConfigDict(extra="forbid")


class LoginRequest(BaseModel):
    user_name: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=1, max_length=128)

    model_config = ConfigDict(extra="forbid")


class UserResponse(BaseModel):
    user_id: UUID
    user_name: str

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class UserProfileResponse(BaseModel):
    user_id: UUID
    user_name: str
    age: int | None = None
    gender: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

    model_config = ConfigDict(extra="forbid")
