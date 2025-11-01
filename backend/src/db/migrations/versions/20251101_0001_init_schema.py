"""init schema

Revision ID: 20251101_0001
Revises:
Create Date: 2025-11-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# --- Revision identifiers ---
revision = "20251101_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "assets",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("ticker", sa.String(20), nullable=False, unique=True),
        sa.Column("name", sa.String(100)),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "simulations",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("command", sa.String(255), nullable=False),
        sa.Column("start_date", sa.Date, nullable=False),
        sa.Column("end_date", sa.Date, nullable=False),
        sa.Column("result_json", sa.JSON, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "metrics",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "simulation_id",
            sa.Integer,
            sa.ForeignKey("simulations.id", ondelete="CASCADE"),
            nullable=False,
            unique=True
        ),
        sa.Column("cagr", sa.Float, nullable=False),
        sa.Column("sharpe", sa.Float, nullable=False),
        sa.Column("max_drawdown", sa.Float, nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "simulation_assets",
        sa.Column("simulation_id", sa.Integer, sa.ForeignKey("simulations.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("asset_id", sa.Integer, sa.ForeignKey("assets.id", ondelete="CASCADE"), primary_key=True),
    )


def downgrade() -> None:
    op.drop_table("simulation_assets")
    op.drop_table("metrics")
    op.drop_table("simulations")
    op.drop_table("assets")
