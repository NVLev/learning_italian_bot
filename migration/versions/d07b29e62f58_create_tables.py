"""create tables

Revision ID: d07b29e62f58
Revises: 
Create Date: 2024-11-01 22:46:30.301388

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd07b29e62f58'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table('themes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('vocabulary',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('italian_word', sa.String(length=50), nullable=False),
    sa.Column('rus_word', sa.String(length=50), nullable=False),
    sa.Column('theme_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['theme_id'], ['themes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )



def downgrade() -> None:

    op.drop_table('vocabulary')
    op.drop_table('themes')

