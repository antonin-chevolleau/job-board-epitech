"""ORM models, mirroring sql/schemas.sql (the SQL file stays the source of truth)."""

from app.core.database import Base
from app.models.advertisement import CONTRACT_TYPES, Advertisement
from app.models.company import Company
from app.models.job_application import APPLICATION_STATUSES, JobApplication
from app.models.user import USER_ROLES, User

__all__ = [
    "APPLICATION_STATUSES",
    "CONTRACT_TYPES",
    "USER_ROLES",
    "Advertisement",
    "Base",
    "Company",
    "JobApplication",
    "User",
]
