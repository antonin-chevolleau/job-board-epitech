import enum
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DECIMAL, TIMESTAMP, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# Imports réservés au typage : évitent un import circulaire à l'exécution.
if TYPE_CHECKING:
    from app.models.application import Application
    from app.models.company import Company


# Valeurs possibles de la colonne ENUM `contract_type`.
# Les valeurs doivent être identiques à celles définies dans MySQL.
class ContractType(enum.Enum):
    cdi = "cdi"
    cdd = "cdd"
    alternance = "alternance"
    stage = "stage"
    freelance = "freelance"
    interim = "interim"


# Valeurs possibles de la colonne ENUM `status`
class AdvertisementStatus(enum.Enum):
    draft = "draft"
    published = "published"
    archived = "archived"


# Représente la table `advertisements` (déjà créée dans Aiven).
# Ce modèle ne crée rien : il décrit la table pour que SQLAlchemy sache la lire.
# Une instance de cette classe = une ligne de la table.
class Advertisement(Base):
    __tablename__ = "advertisements"

    # Mapped[...] = type Python de la valeur ; mapped_column(...) = type SQL.
    # `Mapped[X | None]` correspond à une colonne qui accepte NULL.
    id: Mapped[int] = mapped_column(INTEGER(unsigned=True), primary_key=True)
    title: Mapped[str] = mapped_column(String(150))
    short_description: Mapped[str] = mapped_column(String(300))
    full_description: Mapped[str] = mapped_column(Text)
    salary: Mapped[Decimal | None] = mapped_column(DECIMAL(10, 2))
    location: Mapped[str | None] = mapped_column(String(150))
    working_time: Mapped[str | None] = mapped_column(String(50))
    # values_callable : stocke la valeur ("cdi") et non le nom de l'enum Python
    contract_type: Mapped[ContractType | None] = mapped_column(
        Enum(ContractType, values_callable=lambda e: [m.value for m in e])
    )
    status: Mapped[AdvertisementStatus] = mapped_column(
        Enum(AdvertisementStatus, values_callable=lambda e: [m.value for m in e])
    )
    # ForeignKey : clé étrangère vers companies.id (déjà présente en base)
    company_id: Mapped[int] = mapped_column(
        INTEGER(unsigned=True), ForeignKey("companies.id", ondelete="CASCADE")
    )
    # created_at / updated_at sont remplis automatiquement par MySQL
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP)

    # relationship : navigation entre objets (advertisement.company, ...),
    # sans colonne supplémentaire en base.
    company: Mapped["Company"] = relationship(back_populates="advertisements")
    applications: Mapped[list["Application"]] = relationship(
        back_populates="advertisement", passive_deletes=True
    )
