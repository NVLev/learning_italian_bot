"""fix datetime timezone in training_sessions

Revision ID: c7c179b8c8ce
Revises: e75f48ff0d4f
Create Date: 2025-10-27 21:36:58.447287

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c7c179b8c8ce"
down_revision: Union[str, None] = "e75f48ff0d4f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('training_sessions', 'started_at',
                    type_=sa.DateTime(timezone=True),
                    postgresql_using='started_at AT TIME ZONE \'UTC\'')

    op.alter_column('training_sessions', 'completed_at',
                    type_=sa.DateTime(timezone=True),
                    postgresql_using='completed_at AT TIME ZONE \'UTC\'')


def downgrade() -> None:
    op.alter_column('training_sessions', 'started_at',
                    type_=sa.DateTime(timezone=False))

    op.alter_column('training_sessions', 'completed_at',
                    type_=sa.DateTime(timezone=False))
