from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.orm import joinedload

from app.api.deps import AdminUser, DbSession, OptionalUser, require_admin
from app.api.errors import commit, get_or_404
from app.api.pagination import PageQuery, paginate
from app.api.rate_limit import apply_rate_limit
from app.models import Advertisement, JobApplication, User
from app.schemas import (
    AdvertisementIn,
    AdvertisementOut,
    AdvertisementSummary,
    AdvertisementUpdate,
    ApplicationReceipt,
    ApplyIn,
    ContractType,
    Page,
)
from app.services.emailer import notify_new_application

router = APIRouter(prefix="/advertisements", tags=["advertisements"])
admin_only = [Depends(require_admin)]


def _is_admin(user) -> bool:
    return user is not None and user.role == "admin"


@router.get("", response_model=Page[AdvertisementSummary])
def list_advertisements(
    db: DbSession,
    user: OptionalUser,
    params: PageQuery,
    q: str | None = None,
    location: str | None = None,
    contract_type: ContractType | None = None,
    company_id: int | None = None,
    is_active: Annotated[
        bool | None,
        Query(description="Admins only: other users only ever see active ads"),
    ] = None,
):
    """List advertisements. `q` searches title and short description."""
    stmt = select(Advertisement)
    if _is_admin(user):
        if is_active is not None:
            stmt = stmt.where(Advertisement.is_active == is_active)
    else:
        stmt = stmt.where(Advertisement.is_active.is_(True))
    if q:
        stmt = stmt.where(
            or_(
                Advertisement.title.contains(q, autoescape=True),
                Advertisement.short_description.contains(q, autoescape=True),
            )
        )
    if location:
        stmt = stmt.where(Advertisement.location.contains(location, autoescape=True))
    if contract_type:
        stmt = stmt.where(Advertisement.contract_type == contract_type)
    if company_id:
        stmt = stmt.where(Advertisement.company_id == company_id)
    stmt = stmt.order_by(Advertisement.created_at.desc(), Advertisement.id.desc())
    return paginate(db, stmt, params, joinedload(Advertisement.company))


@router.get("/{advertisement_id}", response_model=AdvertisementOut)
def get_advertisement(advertisement_id: int, db: DbSession, user: OptionalUser):
    ad = get_or_404(db, Advertisement, advertisement_id)
    if not ad.is_active and not _is_admin(user):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Advertisement not found")
    return ad


@router.post(
    "", response_model=AdvertisementOut, status_code=status.HTTP_201_CREATED
)
def create_advertisement(data: AdvertisementIn, db: DbSession, admin: AdminUser):
    values = data.model_dump()
    if values["user_id"] is None:
        values["user_id"] = admin.id
    ad = Advertisement(**values)
    db.add(ad)
    commit(db)
    db.refresh(ad)
    return ad


@router.put(
    "/{advertisement_id}", response_model=AdvertisementOut, dependencies=admin_only
)
def update_advertisement(
    advertisement_id: int, data: AdvertisementUpdate, db: DbSession
):
    ad = get_or_404(db, Advertisement, advertisement_id)
    for field, value in data.model_dump().items():
        setattr(ad, field, value)
    commit(db)
    db.refresh(ad)
    return ad


@router.delete(
    "/{advertisement_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=admin_only,
)
def delete_advertisement(advertisement_id: int, db: DbSession):
    """Also deletes the applications made to this advertisement."""
    db.delete(get_or_404(db, Advertisement, advertisement_id))
    commit(db)


@router.post(
    "/{advertisement_id}/applications",
    response_model=ApplicationReceipt,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(apply_rate_limit)],
    responses={429: {"description": "Too many applications from this IP"}},
)
def apply_to_advertisement(
    advertisement_id: int,
    data: ApplyIn,
    db: DbSession,
    user: OptionalUser,
    background_tasks: BackgroundTasks,
):
    """Apply to an advertisement, anonymously or as a logged-in user.

    Logged-in users may omit name and phone (they default to the profile) and
    always apply with the email of their account. An anonymous visitor cannot
    use the email of an existing account. One application per email and ad.
    The ad owner is notified by email in the background when SMTP is configured.
    """
    ad = get_or_404(db, Advertisement, advertisement_id)
    if not ad.is_active:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Advertisement not found")

    if user is not None:
        values = {
            "applicant_name": data.applicant_name or f"{user.first_name} {user.last_name}",
            "applicant_email": user.email,
            "applicant_phone": data.applicant_phone or user.phone,
        }
        already = db.scalar(
            select(JobApplication.id).where(
                JobApplication.advertisement_id == ad.id,
                JobApplication.user_id == user.id,
            )
        )
        if already is not None:
            raise HTTPException(
                status.HTTP_409_CONFLICT, "You already applied to this advertisement"
            )
    else:
        values = {
            "applicant_name": data.applicant_name,
            "applicant_email": data.applicant_email,
            "applicant_phone": data.applicant_phone,
        }
        missing = [k.removeprefix("applicant_") for k, v in values.items() if not v]
        if missing:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_CONTENT,
                f"Missing fields for anonymous application: {', '.join(missing)}",
            )
        if db.scalar(select(User.id).where(User.email == data.applicant_email)):
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "This email belongs to an account: log in to apply",
            )

    if db.scalar(
        select(JobApplication.id).where(
            JobApplication.advertisement_id == ad.id,
            JobApplication.applicant_email == values["applicant_email"],
        )
    ):
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "An application with this email already exists for this advertisement",
        )

    application = JobApplication(
        advertisement_id=ad.id,
        user_id=user.id if user else None,
        message=data.message,
        **values,
    )
    db.add(application)
    commit(db)
    db.refresh(application)
    background_tasks.add_task(notify_new_application, application.id)
    return application
