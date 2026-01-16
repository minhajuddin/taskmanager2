"""add due_date to tasks

Revision ID: 613de66df578
Revises: 2af04ce18000
Create Date: 2026-01-16 15:03:28.042810

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '613de66df578'
down_revision: Union[str, Sequence[str], None] = '2af04ce18000'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "tasks",
        sa.Column("due_date", sa.Date, nullable=True)
    )


def downgrade():
    op.drop_column("tasks", "due_date")
