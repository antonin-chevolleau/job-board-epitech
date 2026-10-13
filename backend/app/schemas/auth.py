from typing import Annotated

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import Password, Phone, UserName


class RegisterIn(BaseModel):
    """Public sign-up: always creates a plain `user` account."""

    user_name: UserName
    first_name: Annotated[str, Field(min_length=1, max_length=100)]
    last_name: Annotated[str, Field(min_length=1, max_length=100)]
    email: EmailStr
    phone: Phone
    password: Password


class ProfileUpdate(BaseModel):
    """Self-service profile update (role and company cannot be changed here)."""

    user_name: UserName
    first_name: Annotated[str, Field(min_length=1, max_length=100)]
    last_name: Annotated[str, Field(min_length=1, max_length=100)]
    email: EmailStr
    phone: Phone
    new_password: Password | None = None
    current_password: str | None = Field(
        default=None, description="Required when `new_password` is set"
    )


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int
