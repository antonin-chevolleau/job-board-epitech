import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import TIMESTAMP, Enum, FetchedValue, String
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# Import réservé au typage : évite un import circulaire à l'exécution.
if TYPE_CHECKING:
    from app.models.application import Application


# Valeurs possibles de la colonne ENUM `role`
class PersonRole(enum.Enum):
    user = "user"
    admin = "admin"


# Représente la table `people` (déjà créée dans Aiven).
class Person(Base):
    __tablename__ = "people"

    id: Mapped[int] = mapped_column(INTEGER(unsigned=True), primary_key=True)
    firstname: Mapped[str] = mapped_column(String(50))
    lastname: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    phone: Mapped[str | None] = mapped_column(String(20))
    # server_default=FetchedValue() : valeur par défaut posée par MySQL
    # (« user ») quand on n'en fournit pas ; SQLAlchemy n'envoie pas NULL.
    role: Mapped[PersonRole] = mapped_column(
        Enum(PersonRole, values_callable=lambda e: [m.value for m in e]),
        server_default=FetchedValue(),
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=FetchedValue()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=FetchedValue(), server_onupdate=FetchedValue()
    )

    # Une personne peut avoir déposé plusieurs candidatures.
    applications: Mapped[list["Application"]] = relationship(
        back_populates="person", passive_deletes=True
    )
