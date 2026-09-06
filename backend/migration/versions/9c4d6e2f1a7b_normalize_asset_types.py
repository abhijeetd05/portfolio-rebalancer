"""normalize approved asset type casing

Revision ID: 9c4d6e2f1a7b
Revises: 7b3c2f1a9d4e
"""

from alembic import op

revision = "9c4d6e2f1a7b"
down_revision = "7b3c2f1a9d4e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for variant, canonical in (
        ("equity", "Equity"),
        ("debt", "Debt"),
        ("precious metal", "Precious Metal"),
        ("crypto", "Crypto"),
    ):
        op.execute(
            "UPDATE assets SET asset_type = "
            f"'{canonical}' WHERE lower(asset_type) = '{variant}'"
        )


def downgrade() -> None:
    pass
