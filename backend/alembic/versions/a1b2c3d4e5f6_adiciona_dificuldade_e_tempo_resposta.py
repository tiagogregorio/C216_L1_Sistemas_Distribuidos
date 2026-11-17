"""adiciona dificuldade e tempo de resposta

Revision ID: a1b2c3d4e5f6
Revises: 56d0baaf5b21
Create Date: 2026-11-07
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "56d0baaf5b21"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("questoes", sa.Column("dificuldade", sa.String(10), nullable=True))
    op.add_column("respostas", sa.Column("tempo_resposta", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("respostas", "tempo_resposta")
    op.drop_column("questoes", "dificuldade")
