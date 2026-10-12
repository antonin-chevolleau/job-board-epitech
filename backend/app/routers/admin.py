"""Same validated, admin-only CRUD contract for the three other resources."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Response
from sqlalchemy import select

from app.models.advertisement import Advertisement, AdvertisementStatus
from app.models.application import Application
from app.models.company import Company
from app.models.person import Person, PersonRole
from app.schemas.advertisement import AdvertisementRead
from app.schemas.application import (
    ApplicationCreate,
    ApplicationRead,
    ApplicationUpdate,
)
from app.schemas.company import CompanyCreate, CompanyRead, CompanyUpdate
from app.schemas.person import PersonCreate, PersonRead, PersonUpdate
from app.security import Admin, Db, OptionalUser

router = APIRouter(tags=["administration"])


def validate_relations(db, data):
    for field, model in [("people_id", Person), ("advertisement_id", Advertisement)]:
        if field in data and db.get(model, data[field]) is None:
            raise HTTPException(404, f"{field} introuvable.")


def add_crud(path, model, create_schema, update_schema, read_schema):
    def get_record(db, record_id):
        record = db.get(model, record_id)
        if record is None:
            raise HTTPException(404, "Enregistrement introuvable.")
        return record

    def list_records(
        db: Db,
        admin: Admin,
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(ge=1, le=100)] = 20,
    ):
        return db.scalars(
            select(model).order_by(model.id).offset(offset).limit(limit)
        ).all()

    def get_one(record_id: int, db: Db, admin: Admin):
        return get_record(db, record_id)

    def create(payload: create_schema, db: Db, admin: Admin):
        data = payload.model_dump()
        validate_relations(db, data)
        if data.get("email"):
            data["email"] = data["email"].lower()
        record = model(**data)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def update(record_id: int, payload: update_schema, db: Db, admin: Admin):
        record = get_record(db, record_id)
        data = payload.model_dump(exclude_unset=True)
        for field, value in data.items():
            if value is None and not model.__table__.columns[field].nullable:
                raise HTTPException(422, f"{field} ne peut pas être null.")
            setattr(
                record, field, value.lower() if field == "email" and value else value
            )
        db.commit()
        db.refresh(record)
        return record

    def delete(record_id: int, db: Db, admin: Admin):
        if model is Person and record_id == admin.id:
            raise HTTPException(
                409, "Vous ne pouvez pas supprimer votre propre compte administrateur."
            )
        db.delete(get_record(db, record_id))
        db.commit()
        return Response(status_code=204)

    for suffix, method, endpoint, schema, code in [
        ("/", "GET", list_records, list[read_schema], 200),
        ("/{record_id}", "GET", get_one, read_schema, 200),
        ("/", "POST", create, read_schema, 201),
        ("/{record_id}", "PATCH", update, read_schema, 200),
        ("/{record_id}", "DELETE", delete, None, 204),
    ]:
        router.add_api_route(
            path + suffix,
            endpoint,
            methods=[method],
            response_model=schema,
            status_code=code,
            name=f"{method.lower()}_{path.strip('/')}_{endpoint.__name__}",
        )


@router.get("/companies/{company_id}/ads", response_model=list[AdvertisementRead])
def company_ads(
    company_id: int,
    db: Db,
    user: OptionalUser,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    if db.get(Company, company_id) is None:
        raise HTTPException(404, "Entreprise introuvable.")
    query = select(Advertisement).where(Advertisement.company_id == company_id)
    if user is None or user.role != PersonRole.admin:
        query = query.where(Advertisement.status == AdvertisementStatus.published)
    return db.scalars(
        query.order_by(Advertisement.id).offset(offset).limit(limit)
    ).all()


add_crud("/companies", Company, CompanyCreate, CompanyUpdate, CompanyRead)
add_crud("/people", Person, PersonCreate, PersonUpdate, PersonRead)
add_crud(
    "/applications", Application, ApplicationCreate, ApplicationUpdate, ApplicationRead
)
