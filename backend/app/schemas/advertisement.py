from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from app.schemas.common import Id, LongText, ORMModel
from app.schemas.company import CompanySummary

ContractType = Literal["CDI", "CDD", "Stage", "Alternance", "Freelance"]

_Location = Annotated[str, Field(max_length=150)]
_Salary = Annotated[float, Field(ge=0, lt=10**8)]
_WorkingTime = Annotated[str, Field(max_length=50)]


class _AdvertisementBase(BaseModel):
    """Fields required for both creation and replacement."""

    company_id: Id
    title: Annotated[str, Field(min_length=1, max_length=150)]
    short_description: Annotated[str, Field(min_length=1, max_length=300)]
    full_description: Annotated[LongText, Field(min_length=1)]
    contract_type: ContractType


class AdvertisementIn(_AdvertisementBase):
    """Creation: optional fields have defaults."""

    user_id: Id | None = Field(
        default=None,
        description="Poster; defaults to the authenticated admin on creation",
    )
    location: _Location | None = None
    salary: _Salary | None = None
    working_time: _WorkingTime | None = None
    is_active: bool = True


class AdvertisementUpdate(_AdvertisementBase):
    """Full replacement: every field must be sent (optional ones as null)."""

    user_id: Id | None = Field(description="Poster (null for none)")
    location: _Location | None
    salary: _Salary | None
    working_time: _WorkingTime | None
    is_active: bool


class AdvertisementSummary(ORMModel):
    """Light version used in lists (no full description)."""

    id: int
    title: str
    short_description: str
    location: str | None
    salary: float | None
    contract_type: ContractType
    working_time: str | None
    is_active: bool
    created_at: datetime
    company: CompanySummary


class AdvertisementOut(AdvertisementSummary):
    full_description: str
    company_id: int
    user_id: int | None
    updated_at: datetime
