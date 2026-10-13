from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import Id, ORMModel, Password, Phone, UserName

UserRole = Literal["user", "recruiter", "admin"]


class UserBase(BaseModel):
    user_name: UserName
    first_name: Annotated[str, Field(min_length=1, max_length=100)]
    last_name: Annotated[str, Field(min_length=1, max_length=100)]
    email: EmailStr
    phone: Phone


class UserCreate(UserBase):
    role: UserRole = "user"
    company_id: Id | None = None
    password: Password


class UserUpdate(UserBase):
    """Full replacement: `role` and `company_id` must be sent (`company_id` may be
    null). `password` is the only optional field: omitted, it is left unchanged."""

    role: UserRole
    company_id: Id | None
    password: Password | None = None


class UserOut(ORMModel):
    id: int
    user_name: str
    first_name: str
    last_name: str
    email: str
    phone: str
    role: UserRole
    company_id: int | None
    created_at: datetime
    updated_at: datetime
