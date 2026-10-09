from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.advertisement import AdvertisementStatus, ContractType


# Schéma de LECTURE : décrit la forme du JSON renvoyé par l'API.
# Le modèle SQLAlchemy parle à la base ; le schéma Pydantic parle au client.
# Les deux sont séparés pour contrôler précisément ce qui sort de l'API.
class AdvertisementRead(BaseModel):
    # from_attributes=True : permet à Pydantic de lire directement un objet
    # SQLAlchemy (advertisement.title) et pas seulement un dictionnaire.
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    short_description: str
    full_description: str
    # `X | None` = champ facultatif, renvoyé comme null en JSON si vide
    salary: Decimal | None
    location: str | None
    working_time: str | None
    contract_type: ContractType | None
    status: AdvertisementStatus
    company_id: int
    created_at: datetime
    updated_at: datetime
