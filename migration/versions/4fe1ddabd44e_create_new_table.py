"""create new table

Revision ID: 4fe1ddabd44e
Revises: d07b29e62f58
Create Date: 2024-11-07 22:52:15.397109

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4fe1ddabd44e"
down_revision: Union[str, None] = "d07b29e62f58"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "idiom",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("italian_idiom", sa.String(), nullable=False),
        sa.Column("rus_idiom", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("idiom")

