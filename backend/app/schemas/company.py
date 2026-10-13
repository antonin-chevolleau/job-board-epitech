from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import LongText, ORMModel, Phone

_Address = Annotated[str, Field(max_length=255)]
_Country = Annotated[str, Field(max_length=100)]


class _CompanyBase(BaseModel):
    """Fields required for both creation and replacement."""

    name: Annotated[str, Field(min_length=1, max_length=150)]
    email: EmailStr
    phone: Phone
    city: Annotated[str, Field(min_length=1, max_length=100)]


class CompanyIn(_CompanyBase):
    """Creation: optional fields default to null."""

    description: LongText | None = None
    address: _Address | None = None
    country: _Country | None = None


class CompanyUpdate(_CompanyBase):
    """Full replacement: optional fields must be sent (as null to clear them)."""

    description: LongText | None
    address: _Address | None
    country: _Country | None


class CompanyOut(CompanyIn, ORMModel):
    id: int
    email: str  # no re-validation of stored data
    created_at: datetime
    updated_at: datetime


class CompanySummary(ORMModel):
    id: int
    name: str
    city: str
