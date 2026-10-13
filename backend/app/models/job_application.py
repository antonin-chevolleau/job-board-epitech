from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.advertisement import Advertisement
from app.models.user import User

APPLICATION_STATUSES = ("pending", "reviewed", "accepted", "rejected")


class JobApplication(Base):
    __tablename__ = "job_applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    advertisement_id: Mapped[int] = mapped_column(
        ForeignKey("advertisements.id", ondelete="CASCADE")
    )
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    applicant_name: Mapped[str] = mapped_column(String(200))
    applicant_email: Mapped[str] = mapped_column(String(255))
    applicant_phone: Mapped[str] = mapped_column(String(20))
    message: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(
        Enum(*APPLICATION_STATUSES), default="pending", server_default="pending"
    )
    email_sent_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    advertisement: Mapped[Advertisement] = relationship()
    user: Mapped[User | None] = relationship()
