from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.company import Company
from app.models.user import User

CONTRACT_TYPES = ("CDI", "CDD", "Stage", "Alternance", "Freelance")


class Advertisement(Base):
    __tablename__ = "advertisements"

    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE")
    )
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    title: Mapped[str] = mapped_column(String(150))
    short_description: Mapped[str] = mapped_column(String(300))
    full_description: Mapped[str] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(String(150))
    salary: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    contract_type: Mapped[str] = mapped_column(Enum(*CONTRACT_TYPES))
    working_time: Mapped[str | None] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    company: Mapped[Company] = relationship(back_populates="advertisements")
    user: Mapped[User | None] = relationship()
