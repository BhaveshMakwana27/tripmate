"""create vehicle table

Revision ID: c5a27abb9e9f
Revises: d935ed25877b
Create Date: 2024-08-17 17:28:08.813730

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c5a27abb9e9f'
down_revision: Union[str, None] = 'd935ed25877b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('vehicle',sa.Column('vehicle_id',sa.Integer,primary_key=True),
                                sa.Column('user_id',sa.Integer,sa.ForeignKey('user.user_id',ondelete='CASCADE'),nullable=False),
                                sa.Column('type',sa.String,nullable=False),
                                sa.Column('model',sa.String,nullable=False),
                                sa.Column('seat_capacity',sa.Integer,nullable=False),
                                sa.Column('registration_number',sa.String,nullable=False,unique=True),
                                sa.Column('rc_book_front',sa.String,nullable=False),
                                sa.Column('rc_book_back',sa.String,nullable=False),
                                sa.Column('created_at',sa.TIMESTAMP(timezone=True),server_default=sa.text('now()'),nullable=False),
                                sa.Column('updated_at',sa.TIMESTAMP(timezone=True),server_default=sa.text('now()'),nullable=False),
                                )
    pass


def downgrade() -> None:
    op.drop_table('vehicle')
    pass
