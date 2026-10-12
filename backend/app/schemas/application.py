from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.application import ApplicationStatus


# Schéma de LECTURE : forme du JSON renvoyé par l'API.
class ApplicationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    people_id: int
    advertisement_id: int
    message: str
    status: ApplicationStatus
    created_at: datetime
    updated_at: datetime


# Schéma de CRÉATION : le candidat envoie son message pour une annonce.
# `status` n'y figure pas : une candidature démarre toujours à « pending ».
class ApplicationCreate(BaseModel):
    people_id: int = Field(ge=1)
    advertisement_id: int = Field(ge=1)
    message: str = Field(min_length=1)


# Schéma de MISE À JOUR : seul le statut change (accepted / rejected),
# par exemple par un recruteur ou un admin.
class ApplicationUpdate(BaseModel):
    status: ApplicationStatus
