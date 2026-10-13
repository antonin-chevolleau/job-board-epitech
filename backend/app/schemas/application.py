from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import Id, ORMModel, Phone

ApplicationStatus = Literal["pending", "reviewed", "accepted", "rejected"]

_Message = Annotated[str, Field(min_length=1, max_length=5000)]


class _ApplicationBase(BaseModel):
    """Fields required for both creation and replacement."""

    advertisement_id: Id
    applicant_name: Annotated[str, Field(min_length=1, max_length=200)]
    applicant_email: EmailStr
    applicant_phone: Phone
    message: _Message


class ApplicationIn(_ApplicationBase):
    """Creation: `user_id` and `status` have defaults."""

    user_id: Id | None = None
    status: ApplicationStatus = "pending"


class ApplicationUpdate(_ApplicationBase):
    """Full replacement: `user_id` (nullable) and `status` must be sent."""

    user_id: Id | None
    status: ApplicationStatus


class ApplyIn(BaseModel):
    """Public application. Identity fields are required for anonymous visitors.
    Logged-in users may omit them (name and phone default to the profile); their
    email is always the one of their account."""

    applicant_name: Annotated[str, Field(min_length=1, max_length=200)] | None = None
    applicant_email: EmailStr | None = None
    applicant_phone: Phone | None = None
    message: _Message


class ApplicationReceipt(ORMModel):
    id: int
    advertisement_id: int
    applicant_name: str
    applicant_email: str
    applicant_phone: str
    message: str
    status: ApplicationStatus
    created_at: datetime


class ApplicationOut(ORMModel):
    id: int
    advertisement_id: int
    user_id: int | None
    applicant_name: str
    applicant_email: str
    applicant_phone: str
    message: str
    status: ApplicationStatus
    email_sent_at: datetime | None
    created_at: datetime
    updated_at: datetime
