from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Responsible(Base):
    __tablename__ = "responsible"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    service_links = relationship(
        "ServiceResponsible",
        back_populates="responsible",
        cascade="all, delete-orphan",
    )
    services = relationship(
        "Service",
        secondary="service_responsible",
        back_populates="responsibles",
        viewonly=True,
    )
    notification_logs = relationship("NotificationLog", back_populates="responsible")
