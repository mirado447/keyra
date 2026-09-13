from sqlalchemy import DateTime, ForeignKey, String
from datetime import datetime, timezone
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )

    public_key: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    private_key_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    create_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    developer_id: Mapped[int] = mapped_column(
        ForeignKey("developers.id"),
        nullable=False,
    )