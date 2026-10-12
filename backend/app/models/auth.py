"""Authentication is stored separately: existing people rows stay compatible."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Credential(Base):
    __tablename__ = "credentials"

    people_id: Mapped[int] = mapped_column(
        INTEGER(unsigned=True),
        ForeignKey("people.id", ondelete="CASCADE"),
        primary_key=True,
    )
    password_hash: Mapped[str] = mapped_column(String(255))


class AuthSession(Base):
    __tablename__ = "auth_sessions"

    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    people_id: Mapped[int] = mapped_column(
        INTEGER(unsigned=True), ForeignKey("people.id", ondelete="CASCADE"), index=True
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime)
