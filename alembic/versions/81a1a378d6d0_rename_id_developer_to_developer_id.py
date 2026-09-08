"""rename id_developer to developer_id

Revision ID: 81a1a378d6d0
Revises: b3d980bdf14d
Create Date: 2026-09-08 22:49:19.131373

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '81a1a378d6d0'
down_revision: Union[str, Sequence[str], None] = 'b3d980bdf14d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Rename id_developer column to developer_id."""
    op.alter_column(
        "applications",
        "id_developer",
        new_column_name="developer_id",
    )


def downgrade() -> None:
    """Rename developer_id column back to id_developer."""
    op.alter_column(
        "applications",
        "developer_id",
        new_column_name="id_developer",
    )