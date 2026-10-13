"""Pydantic request / response models, grouped by resource."""

from app.schemas.advertisement import (
    AdvertisementIn,
    AdvertisementOut,
    AdvertisementSummary,
    AdvertisementUpdate,
    ContractType,
)
from app.schemas.application import (
    ApplicationIn,
    ApplicationOut,
    ApplicationReceipt,
    ApplicationStatus,
    ApplicationUpdate,
    ApplyIn,
)
from app.schemas.auth import ProfileUpdate, RegisterIn, TokenOut
from app.schemas.common import Id, LongText, ORMModel, Page, Password, Phone, UserName
from app.schemas.company import CompanyIn, CompanyOut, CompanySummary, CompanyUpdate
from app.schemas.user import UserBase, UserCreate, UserOut, UserRole, UserUpdate

__all__ = [
    "AdvertisementIn",
    "AdvertisementOut",
    "AdvertisementSummary",
    "AdvertisementUpdate",
    "ApplicationIn",
    "ApplicationOut",
    "ApplicationReceipt",
    "ApplicationStatus",
    "ApplicationUpdate",
    "ApplyIn",
    "CompanyIn",
    "CompanyOut",
    "CompanySummary",
    "CompanyUpdate",
    "ContractType",
    "Id",
    "LongText",
    "ORMModel",
    "Page",
    "Password",
    "Phone",
    "ProfileUpdate",
    "RegisterIn",
    "TokenOut",
    "UserBase",
    "UserCreate",
    "UserName",
    "UserOut",
    "UserRole",
    "UserUpdate",
]
