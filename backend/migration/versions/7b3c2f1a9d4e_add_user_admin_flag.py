"""add user admin flag

Revision ID: 7b3c2f1a9d4e
Revises: 47731bc68a08
"""

from alembic import op
import sqlalchemy as sa

revision = "7b3c2f1a9d4e"
down_revision = "47731bc68a08"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("is_admin", sa.Boolean(), server_default="false", nullable=False))


def downgrade() -> None:
    op.drop_column("users", "is_admin")
