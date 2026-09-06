"""add external market-data mapping to assets

Revision ID: a1b2c3d4e5f6
Revises: 9c4d6e2f1a7b
"""

from alembic import op
import sqlalchemy as sa

revision = "a1b2c3d4e5f6"
down_revision = "9c4d6e2f1a7b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("assets", sa.Column("external_provider", sa.String(length=50), nullable=True))
    op.add_column("assets", sa.Column("external_asset_id", sa.String(length=100), nullable=True))


def downgrade() -> None:
    op.drop_column("assets", "external_asset_id")
    op.drop_column("assets", "external_provider")
