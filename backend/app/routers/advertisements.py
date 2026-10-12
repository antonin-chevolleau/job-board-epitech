from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, Response
from sqlalchemy import select

from app.models.advertisement import Advertisement, AdvertisementStatus
from app.models.application import Application
from app.models.company import Company
from app.models.person import Person, PersonRole
from app.schemas.advertisement import (
    AdvertisementCreate,
    AdvertisementRead,
    AdvertisementUpdate,
)
from app.schemas.application import ApplicationRead
from app.schemas.auth import Apply
from app.security import Admin, Db, OptionalUser

router = APIRouter(prefix="/advertisements", tags=["advertisements"])


def visible_ad(advertisement_id, db, user):
    ad = db.get(Advertisement, advertisement_id)
    if ad is None or (
        ad.status != AdvertisementStatus.published
        and (user is None or user.role != PersonRole.admin)
    ):
        raise HTTPException(404, "Annonce introuvable.")
    return ad


@router.get("/", response_model=list[AdvertisementRead])
def list_advertisements(
    db: Db,
    user: OptionalUser,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
):
    query = select(Advertisement)
    if user is None or user.role != PersonRole.admin:
        query = query.where(Advertisement.status == AdvertisementStatus.published)
    return db.scalars(
        query.order_by(Advertisement.id.desc()).offset(offset).limit(limit)
    ).all()


@router.get("/{advertisement_id}", response_model=AdvertisementRead)
def get_advertisement(advertisement_id: int, db: Db, user: OptionalUser):
    return visible_ad(advertisement_id, db, user)


@router.post("/", response_model=AdvertisementRead, status_code=201)
def create_advertisement(payload: AdvertisementCreate, db: Db, admin: Admin):
    if db.get(Company, payload.company_id) is None:
        raise HTTPException(404, "Entreprise introuvable.")
    ad = Advertisement(**payload.model_dump())
    db.add(ad)
    db.commit()
    db.refresh(ad)
    return ad


@router.patch("/{advertisement_id}", response_model=AdvertisementRead)
def update_advertisement(
    advertisement_id: int, payload: AdvertisementUpdate, db: Db, admin: Admin
):
    ad = visible_ad(advertisement_id, db, admin)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(ad, field, value)
    db.commit()
    db.refresh(ad)
    return ad


@router.delete("/{advertisement_id}", status_code=204)
def delete_advertisement(advertisement_id: int, db: Db, admin: Admin):
    db.delete(visible_ad(advertisement_id, db, admin))
    db.commit()
    return Response(status_code=204)


@router.post(
    "/{advertisement_id}/applications", response_model=ApplicationRead, status_code=201
)
def apply(advertisement_id: int, payload: Apply, db: Db, user: OptionalUser):
    ad = visible_ad(advertisement_id, db, user)
    if ad.status != AdvertisementStatus.published:
        raise HTTPException(409, "Cette annonce n’accepte pas de candidatures.")
    person = user
    if person is None:
        if not payload.firstname or not payload.lastname or not payload.email:
            raise HTTPException(400, "Prénom, nom et email sont obligatoires.")
        email = payload.email.lower()
        # Never attach an anonymous request to someone else's account.
        if db.scalar(select(Person).where(Person.email == email)):
            raise HTTPException(
                409,
                "Adresse déjà utilisée : connectez-vous ou contactez l’administrateur.",
            )
        person = Person(
            firstname=payload.firstname,
            lastname=payload.lastname,
            email=email,
            phone=payload.phone,
        )
        db.add(person)
        db.flush()
    if db.scalar(
        select(Application).where(
            Application.people_id == person.id, Application.advertisement_id == ad.id
        )
    ):
        raise HTTPException(409, "Vous avez déjà postulé à cette annonce.")
    application = Application(
        people_id=person.id, advertisement_id=ad.id, message=payload.message
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return application
