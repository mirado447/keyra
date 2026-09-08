from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    token_hash: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    create_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    revoked: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    expire_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("endusers.id"),
        nullable=False,
    )