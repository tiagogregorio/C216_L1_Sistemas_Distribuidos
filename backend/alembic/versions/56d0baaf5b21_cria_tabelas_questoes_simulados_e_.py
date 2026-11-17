"""cria tabelas questoes simulados e respostas

Revision ID: 56d0baaf5b21
Revises:
Create Date: 2026-11-06
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "56d0baaf5b21"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "questoes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ano", sa.Integer(), nullable=False),
        sa.Column("numero", sa.Integer(), nullable=False),
        sa.Column("tipo", sa.String(2), nullable=False),
        sa.Column("enunciado", sa.Text(), nullable=False),
        sa.Column("alternativa_a", sa.Text(), nullable=False),
        sa.Column("alternativa_b", sa.Text(), nullable=False),
        sa.Column("alternativa_c", sa.Text(), nullable=False),
        sa.Column("alternativa_d", sa.Text(), nullable=False),
        sa.Column("alternativa_e", sa.Text(), nullable=False),
        sa.Column("resposta", sa.String(1), nullable=False),
        sa.Column("assunto", sa.String(100), nullable=True),
    )

    op.create_table(
        "simulados",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nome", sa.String(120), nullable=False),
        sa.Column(
            "criado_em",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("finalizado", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("total_questoes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("acertos", sa.Integer(), nullable=True),
        sa.Column("nota", sa.Float(), nullable=True),
    )

    op.create_table(
        "respostas",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "simulado_id",
            sa.Integer(),
            sa.ForeignKey("simulados.id"),
            nullable=False,
        ),
        sa.Column(
            "questao_id",
            sa.Integer(),
            sa.ForeignKey("questoes.id"),
            nullable=False,
        ),
        sa.Column("alternativa_escolhida", sa.String(1), nullable=True),
        sa.Column("correta", sa.Boolean(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("respostas")
    op.drop_table("simulados")
    op.drop_table("questoes")
