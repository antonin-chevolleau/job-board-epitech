from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.person import PersonRole


# Schéma de LECTURE : forme du JSON renvoyé par l'API.
class PersonRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    firstname: str
    lastname: str
    email: str
    phone: str | None
    role: PersonRole
    created_at: datetime
    updated_at: datetime


# Schéma de CRÉATION.
# `role` n'y figure volontairement pas : un client ne doit pas pouvoir
# s'attribuer le rôle admin à l'inscription (la base applique « user » par défaut).
class PersonCreate(BaseModel):
    firstname: str = Field(min_length=1, max_length=50)
    lastname: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=255)
    phone: str | None = Field(default=None, max_length=20)


# Schéma de MISE À JOUR PARTIELLE : tous les champs sont facultatifs.
# Le rôle n'est pas modifiable ici non plus.
class PersonUpdate(BaseModel):
    firstname: str | None = Field(default=None, min_length=1, max_length=50)
    lastname: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
