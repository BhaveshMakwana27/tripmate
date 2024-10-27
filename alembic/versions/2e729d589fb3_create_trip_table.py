"""create trip table

Revision ID: 2e729d589fb3
Revises: 9716c053e926
Create Date: 2024-08-21 01:38:59.268254

"""
from typing import Sequence, Union
from app import enums
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2e729d589fb3'
down_revision: Union[str, None] = '9716c053e926'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('trip',sa.Column('trip_id',sa.Integer,primary_key=True),
                            sa.Column('user_id',sa.Integer,sa.ForeignKey('user.user_id',ondelete='CASCADE'),nullable=False),
                            sa.Column('vehicle_id',sa.Integer,sa.ForeignKey('vehicle.vehicle_id',ondelete='CASCADE'),nullable=False),
                            sa.Column('source_address_line',sa.String,nullable=False),
                            sa.Column('source_city',sa.String,nullable=False),
                            sa.Column('source_state',sa.String,nullable=False),
                            sa.Column('source_country',sa.String,nullable=False),
                            sa.Column('source_pincode',sa.String,nullable=False),
                            sa.Column('destination_address_line',sa.String,nullable=False),
                            sa.Column('destination_city',sa.String,nullable=False),
                            sa.Column('destination_state',sa.String,nullable=False),
                            sa.Column('destination_country',sa.String,nullable=False),
                            sa.Column('destination_pincode',sa.String,nullable=False),
                            sa.Column('seats_available',sa.Integer,nullable=False),
                            sa.Column('fees_per_person',sa.Integer,nullable=False),
                            sa.Column('status',sa.Enum(enums.TripStatus),nullable=False,server_default=enums.TripStatus.UPCOMING.value),
                            sa.Column('start_time',sa.TIMESTAMP(timezone=True),nullable=False),
                            sa.Column('end_time',sa.TIMESTAMP(timezone=True),nullable=False),
                            sa.Column('duration',sa.Interval, sa.Computed('end_time - start_time')),
                            sa.Column('created_at',sa.TIMESTAMP(timezone=True),server_default=sa.text('now()')),
                            sa.Column('updated_at',sa.TIMESTAMP(timezone=True),server_default=sa.text('now()'))
                            )
    pass


def downgrade() -> None:
    op.drop_table('trip')
    pass
