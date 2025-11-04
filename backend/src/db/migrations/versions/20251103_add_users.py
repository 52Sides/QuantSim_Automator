from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=120), nullable=False, unique=True, index=True),
        sa.Column("hashed_password", sa.String(length=256), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.add_column("simulations", sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True))

def downgrade():
    op.drop_column("simulations", "user_id")
    op.drop_table("users")
