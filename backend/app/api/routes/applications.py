from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import or_, select

from app.api.deps import DbSession, require_admin
from app.api.errors import commit, get_or_404
from app.api.pagination import PageQuery, paginate
from app.models import JobApplication
from app.schemas import (
    ApplicationIn,
    ApplicationOut,
    ApplicationStatus,
    ApplicationUpdate,
    Page,
)

router = APIRouter(
    prefix="/applications", tags=["applications"], dependencies=[Depends(require_admin)]
)


@router.get("", response_model=Page[ApplicationOut])
def list_applications(
    db: DbSession,
    params: PageQuery,
    q: str | None = None,
    advertisement_id: int | None = None,
    user_id: int | None = None,
    status_: Annotated[ApplicationStatus | None, Query(alias="status")] = None,
):
    """List applications; `q` searches applicant name and email."""
    stmt = select(JobApplication)
    if q:
        stmt = stmt.where(
            or_(
                JobApplication.applicant_name.contains(q, autoescape=True),
                JobApplication.applicant_email.contains(q, autoescape=True),
            )
        )
    if advertisement_id:
        stmt = stmt.where(JobApplication.advertisement_id == advertisement_id)
    if user_id:
        stmt = stmt.where(JobApplication.user_id == user_id)
    if status_:
        stmt = stmt.where(JobApplication.status == status_)
    stmt = stmt.order_by(JobApplication.created_at.desc(), JobApplication.id.desc())
    return paginate(db, stmt, params)


@router.get("/{application_id}", response_model=ApplicationOut)
def get_application(application_id: int, db: DbSession):
    return get_or_404(db, JobApplication, application_id)


@router.post("", response_model=ApplicationOut, status_code=status.HTTP_201_CREATED)
def create_application(data: ApplicationIn, db: DbSession):
    application = JobApplication(**data.model_dump())
    db.add(application)
    commit(db)
    db.refresh(application)
    return application


@router.put("/{application_id}", response_model=ApplicationOut)
def update_application(
    application_id: int, data: ApplicationUpdate, db: DbSession
):
    application = get_or_404(db, JobApplication, application_id)
    for field, value in data.model_dump().items():
        setattr(application, field, value)
    commit(db)
    db.refresh(application)
    return application


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(application_id: int, db: DbSession):
    db.delete(get_or_404(db, JobApplication, application_id))
    commit(db)
