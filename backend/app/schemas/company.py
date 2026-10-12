from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# Schéma de LECTURE : forme du JSON renvoyé par l'API.
class CompanyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None
    email: str | None
    phone: str | None
    address: str | None
    city: str | None
    country: str | None
    created_at: datetime
    updated_at: datetime


# Schéma de CRÉATION : seul `name` est obligatoire (et unique en base).
# EmailStr vérifie le format de l'adresse (nécessite email-validator).
class CompanyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = None
    email: EmailStr | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    address: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)


# Schéma de MISE À JOUR PARTIELLE : tous les champs sont facultatifs.
class CompanyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = None
    email: EmailStr | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    address: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=100)
    country: str | None = Field(default=None, max_length=100)
