from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.advertisement import Advertisement
from app.models.company import Company
from app.schemas.advertisement import (
    AdvertisementCreate,
    AdvertisementRead,
    AdvertisementUpdate,
)

# Un router regroupe les routes d'une même ressource.
# prefix : toutes les routes ci-dessous commencent par /advertisements
# tags : regroupe ces routes dans la doc auto (/docs)
router = APIRouter(prefix="/advertisements", tags=["advertisements"])


# GET /advertisements : renvoie toutes les annonces.
# response_model : FastAPI convertit chaque objet SQLAlchemy en AdvertisementRead
# (donc en JSON) et documente la forme de la réponse dans /docs.
@router.get("/", response_model=list[AdvertisementRead])
def list_advertisements(db: Annotated[Session, Depends(get_db)]):
    # select(Advertisement) = SELECT * FROM advertisements
    # scalars().all() = récupère toutes les lignes sous forme d'objets Advertisement
    return db.scalars(select(Advertisement)).all()


# GET /advertisements/{advertisement_id} : renvoie une annonce par son id.
# {advertisement_id} est un paramètre de chemin : FastAPI le convertit en int
# (422 automatique si ce n'est pas un entier).
@router.get("/{advertisement_id}", response_model=AdvertisementRead)
def get_advertisement(advertisement_id: int, db: Annotated[Session, Depends(get_db)]):
    # db.get(Model, pk) = SELECT ... WHERE id = :id, renvoie None si absent
    advertisement = db.get(Advertisement, advertisement_id)
    if advertisement is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    return advertisement


# POST /advertisements : crée une annonce.
# Le corps JSON est validé par AdvertisementCreate (422 si invalide).
# status_code=201 : « Created », le code HTTP standard pour une création.
@router.post("/", response_model=AdvertisementRead, status_code=status.HTTP_201_CREATED)
def create_advertisement(
    payload: AdvertisementCreate, db: Annotated[Session, Depends(get_db)]
):
    # On vérifie l'entreprise avant d'insérer : sans ça, la clé étrangère
    # ferait échouer l'INSERT et le client recevrait une erreur 500.
    if db.get(Company, payload.company_id) is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Company not found",
        )
    # model_dump() : schéma Pydantic -> dict, dépacké en arguments du modèle
    advertisement = Advertisement(**payload.model_dump())
    db.add(advertisement)
    db.commit()
    # refresh : relit la ligne pour récupérer les valeurs générées par MySQL
    # (id, created_at, updated_at)
    db.refresh(advertisement)
    return advertisement


# PATCH /advertisements/{advertisement_id} : modifie une annonce (partiellement).
# Seuls les champs présents dans le JSON sont modifiés.
@router.patch("/{advertisement_id}", response_model=AdvertisementRead)
def update_advertisement(
    advertisement_id: int,
    payload: AdvertisementUpdate,
    db: Annotated[Session, Depends(get_db)],
):
    advertisement = db.get(Advertisement, advertisement_id)
    if advertisement is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    # exclude_unset=True : ignore les champs que le client n'a pas envoyés
    # (différent de « envoyés à null », qui permet d'effacer un champ facultatif)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(advertisement, field, value)
    db.commit()
    db.refresh(advertisement)
    return advertisement


# DELETE /advertisements/{advertisement_id} : supprime une annonce.
# 204 « No Content » : succès, sans corps de réponse. Les candidatures liées
# sont supprimées par MySQL (ON DELETE CASCADE).
@router.delete("/{advertisement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_advertisement(
    advertisement_id: int, db: Annotated[Session, Depends(get_db)]
):
    advertisement = db.get(Advertisement, advertisement_id)
    if advertisement is None:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    db.delete(advertisement)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
