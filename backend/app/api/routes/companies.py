from fastapi import APIRouter, Depends, status
from sqlalchemy import or_, select

from app.api.deps import DbSession, require_admin
from app.api.errors import commit, get_or_404
from app.api.pagination import PageQuery, paginate
from app.models import Company
from app.schemas import CompanyIn, CompanyOut, CompanyUpdate, Page

router = APIRouter(prefix="/companies", tags=["companies"])
admin_only = [Depends(require_admin)]


@router.get("", response_model=Page[CompanyOut])
def list_companies(db: DbSession, params: PageQuery, q: str | None = None):
    """List companies; `q` searches name and city."""
    stmt = select(Company)
    if q:
        stmt = stmt.where(
            or_(Company.name.contains(q, autoescape=True), Company.city.contains(q, autoescape=True))
        )
    return paginate(db, stmt.order_by(Company.name, Company.id), params)


@router.get("/{company_id}", response_model=CompanyOut)
def get_company(company_id: int, db: DbSession):
    return get_or_404(db, Company, company_id)


@router.post(
    "", response_model=CompanyOut, status_code=status.HTTP_201_CREATED, dependencies=admin_only
)
def create_company(data: CompanyIn, db: DbSession):
    company = Company(**data.model_dump())
    db.add(company)
    commit(db)
    db.refresh(company)
    return company


@router.put("/{company_id}", response_model=CompanyOut, dependencies=admin_only)
def update_company(company_id: int, data: CompanyUpdate, db: DbSession):
    company = get_or_404(db, Company, company_id)
    for field, value in data.model_dump().items():
        setattr(company, field, value)
    commit(db)
    db.refresh(company)
    return company


@router.delete(
    "/{company_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=admin_only
)
def delete_company(company_id: int, db: DbSession):
    """Also deletes the company's advertisements (and their applications)."""
    db.delete(get_or_404(db, Company, company_id))
    commit(db)
