from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

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


# Schéma de CRÉATION : décrit le JSON que le client envoie (POST).
# FastAPI le valide avant d'appeler la route : si une règle n'est pas respectée,
# le client reçoit automatiquement une erreur 422.
# id, created_at et updated_at n'y figurent pas : ils sont générés par la base.
class AdvertisementCreate(BaseModel):
    # Field(...) ajoute des règles : longueur min/max (alignées sur les
    # colonnes VARCHAR), ge=0 = « supérieur ou égal à 0 ».
    title: str = Field(min_length=1, max_length=150)
    short_description: str = Field(min_length=1, max_length=300)
    full_description: str = Field(min_length=1)
    salary: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    location: str | None = Field(default=None, max_length=150)
    working_time: str | None = Field(default=None, max_length=50)
    contract_type: ContractType | None = None
    # Une annonce est un brouillon tant qu'on ne la publie pas explicitement.
    status: AdvertisementStatus = AdvertisementStatus.draft
    company_id: int = Field(ge=1)


# Schéma de MISE À JOUR PARTIELLE (PATCH) : tous les champs sont facultatifs.
# Dans la route, on utilisera model_dump(exclude_unset=True) pour ne modifier
# que les champs réellement envoyés par le client.
# Pas de company_id : on ne change pas l'entreprise d'une annonce existante.
class AdvertisementUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=150)
    short_description: str | None = Field(default=None, min_length=1, max_length=300)
    full_description: str | None = Field(default=None, min_length=1)
    salary: Decimal | None = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    location: str | None = Field(default=None, max_length=150)
    working_time: str | None = Field(default=None, max_length=50)
    contract_type: ContractType | None = None
    status: AdvertisementStatus | None = None

    # Ces colonnes sont NOT NULL en base : on peut ne pas les envoyer (champ
    # absent = inchangé), mais pas les envoyer à null. Ce validateur ne
    # s'exécute que si le champ est présent dans le JSON.
    @field_validator("title", "short_description", "full_description", "status")
    @classmethod
    def reject_null(cls, value):
        if value is None:
            raise ValueError("ne peut pas être null")
        return value
