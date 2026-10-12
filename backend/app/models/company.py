from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import TIMESTAMP, String, Text
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# Import réservé au typage : évite un import circulaire à l'exécution.
if TYPE_CHECKING:
    from app.models.advertisement import Advertisement


# Représente la table `companies` (déjà créée dans Aiven).
class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(INTEGER(unsigned=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(150), unique=True)
    description: Mapped[str | None] = mapped_column(Text)
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(20))
    address: Mapped[str | None] = mapped_column(String(255))
    city: Mapped[str | None] = mapped_column(String(100))
    country: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP)

    # Une entreprise a plusieurs annonces (côté « un » de la relation).
    # passive_deletes=True : on laisse MySQL appliquer ON DELETE CASCADE.
    advertisements: Mapped[list["Advertisement"]] = relationship(
        back_populates="company", passive_deletes=True
    )
