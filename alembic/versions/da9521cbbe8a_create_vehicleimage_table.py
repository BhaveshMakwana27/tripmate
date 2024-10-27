"""create vehicleimage table

Revision ID: da9521cbbe8a
Revises: c5a27abb9e9f
Create Date: 2024-08-17 17:49:55.494146

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'da9521cbbe8a'
down_revision: Union[str, None] = 'c5a27abb9e9f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('vehicle_image',
                    sa.Column('image_id',sa.Integer,primary_key=True),
                    sa.Column('vehicle_id',sa.Integer,sa.ForeignKey('vehicle.vehicle_id',ondelete='CASCADE'),nullable=False),
                    sa.Column('image_path',sa.String,nullable=False)
                    )
                    
    pass


def downgrade() -> None:
    op.drop_table('vehicle_image')
    pass
