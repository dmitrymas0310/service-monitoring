from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class NotificationLog(Base):
    __tablename__ = "notification_log"
    __table_args__ = (
        CheckConstraint(
            "status IN ('SENT', 'FAILED')",
            name="ck_notification_log_status",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    service_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("service.id"),
        nullable=False,
    )
    endpoint_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("endpoint.id"),
        nullable=False,
    )
    check_result_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("check_result.id"),
        nullable=False,
    )
    responsible_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("responsible.id"),
        nullable=False,
    )
    channel: Mapped[str] = mapped_column(String(50), nullable=False, default="EMAIL")
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    service = relationship("Service", back_populates="notification_logs")
    endpoint = relationship("Endpoint", back_populates="notification_logs")
    check_result = relationship("CheckResult", back_populates="notification_logs")
    responsible = relationship("Responsible", back_populates="notification_logs")
