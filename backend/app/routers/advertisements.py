from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.advertisement import Advertisement
from app.schemas.advertisement import AdvertisementRead

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
