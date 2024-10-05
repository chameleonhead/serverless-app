"""create contacts table

Revision ID: ee3ba0b8ba14
Revises:
Create Date: 2024-10-05 18:59:54.620472

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ee3ba0b8ba14"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "contacts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("first", sa.String()),
        sa.Column("last", sa.String()),
        sa.Column("avatar", sa.String()),
        sa.Column("twitter", sa.String()),
        sa.Column("notes", sa.String()),
        sa.Column("favorite", sa.Boolean()),
        sa.Column("createdAt", sa.DateTime()),
    )


def downgrade() -> None:
    op.drop_table("contacts")
