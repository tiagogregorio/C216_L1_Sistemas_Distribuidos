"""adiciona ciclo de cobertura

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-11-09
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ciclo_cobertura",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("valor", sa.Integer(), nullable=False, server_default="1"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.execute("INSERT INTO ciclo_cobertura (id, valor) VALUES (1, 1)")

    op.add_column(
        "simulados",
        sa.Column("ciclo", sa.Integer(), nullable=False, server_default="1"),
    )


def downgrade() -> None:
    op.drop_column("simulados", "ciclo")
    op.drop_table("ciclo_cobertura")
