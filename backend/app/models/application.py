import enum
from datetime import datetime

from sqlalchemy import TIMESTAMP, Enum, FetchedValue, ForeignKey, Text
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.clock import utcnow
from app.database import Base
from app.models.advertisement import Advertisement
from app.models.person import Person


# Valeurs possibles de la colonne ENUM `status`
class ApplicationStatus(enum.Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"


# Représente la table `applications` (déjà créée dans Aiven).
# Une candidature relie une personne (people) à une annonce (advertisements).
class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(INTEGER(unsigned=True), primary_key=True)
    # ForeignKey : indique à SQLAlchemy la clé étrangère (déjà présente en base)
    people_id: Mapped[int] = mapped_column(
        INTEGER(unsigned=True), ForeignKey("people.id", ondelete="CASCADE")
    )
    advertisement_id: Mapped[int] = mapped_column(
        INTEGER(unsigned=True), ForeignKey("advertisements.id", ondelete="CASCADE")
    )
    message: Mapped[str] = mapped_column(Text)
    # Valeur par défaut (« pending ») posée par MySQL, cf. Person.role
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus, values_callable=lambda e: [m.value for m in e]),
        default=ApplicationStatus.pending,
        server_default="pending",
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=utcnow, server_default=FetchedValue()
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        default=utcnow,
        onupdate=utcnow,
        server_default=FetchedValue(),
        server_onupdate=FetchedValue(),
    )

    person: Mapped[Person] = relationship(back_populates="applications")
    advertisement: Mapped[Advertisement] = relationship(back_populates="applications")
