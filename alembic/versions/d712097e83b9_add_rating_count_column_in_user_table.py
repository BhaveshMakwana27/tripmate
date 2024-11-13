"""add rating_count column in User table

Revision ID: d712097e83b9
Revises: 6458b28ac1c7
Create Date: 2024-11-13 20:28:17.796738

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd712097e83b9'
down_revision: Union[str, None] = '6458b28ac1c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('user',sa.Column('rating_count',sa.Integer,nullable=False,server_default='0'))
    pass


def downgrade() -> None:
    op.drop_column('user','rating_count')
    pass