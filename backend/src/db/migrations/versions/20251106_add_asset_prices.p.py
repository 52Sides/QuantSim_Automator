from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        "asset_prices",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ticker", sa.String(length=16), nullable=False, index=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("open", sa.Float(), nullable=True),
        sa.Column("high", sa.Float(), nullable=True),
        sa.Column("low", sa.Float(), nullable=True),
        sa.Column("close", sa.Float(), nullable=True),
        sa.Column("volume", sa.Float(), nullable=True),
        sa.Column("volume", sa.Float(), nullable=True),
        sa.Column("inserted_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.UniqueConstraint('ticker', 'date', name='uq_asset_ticker_date'),
    )
    op.create_index('ix_asset_ticker_date', 'asset_prices', ['ticker', 'date'])


def downgrade():
    op.drop_index('ix_asset_ticker_date', table_name='asset_prices')
    op.drop_table('asset_prices')