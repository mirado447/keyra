"""rename id_user and id_app to user_id and app_id

Revision ID: 74fe8e1298b8
Revises: 81a1a378d6d0
Create Date: 2026-09-08 23:06:20.188118
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "74fe8e1298b8"
down_revision: Union[str, Sequence[str], None] = "81a1a378d6d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Rename foreign key columns."""

    op.alter_column(
        "endusers",
        "id_app",
        new_column_name="app_id",
    )

    op.alter_column(
        "refresh_tokens",
        "id_user",
        new_column_name="user_id",
    )


def downgrade() -> None:
    """Restore previous foreign key column names."""

    op.alter_column(
        "refresh_tokens",
        "user_id",
        new_column_name="id_user",
    )

    op.alter_column(
        "endusers",
        "app_id",
        new_column_name="id_app",
    )