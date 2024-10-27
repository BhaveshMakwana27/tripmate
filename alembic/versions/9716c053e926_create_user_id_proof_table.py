"""create user_id_proof table

Revision ID: 9716c053e926
Revises: da9521cbbe8a
Create Date: 2024-08-19 14:49:24.145794

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9716c053e926'
down_revision: Union[str, None] = 'da9521cbbe8a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('user_id_proof',sa.Column('user_id',sa.Integer,sa.ForeignKey('user.user_id',ondelete='CASCADE'),primary_key=True),
                                    sa.Column('aadhar_number',sa.String(16),unique=True,nullable=False),
                                    sa.Column('aadhar_card_front',sa.String,nullable=False),
                                    sa.Column('aadhar_card_back',sa.String,nullable=False),
                                    sa.Column('license_front',sa.String,nullable=False),
                                    sa.Column('license_back',sa.String,nullable=False)
                    )
    pass


def downgrade() -> None:
    op.drop_table('user_id_proof')
    pass
