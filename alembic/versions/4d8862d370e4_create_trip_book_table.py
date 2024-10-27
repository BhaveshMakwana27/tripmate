"""create trip_book table

Revision ID: 4d8862d370e4
Revises: 2e729d589fb3
Create Date: 2024-09-03 05:55:22.168767

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from app import enums

# revision identifiers, used by Alembic.
revision: str = '4d8862d370e4'
down_revision: Union[str, None] = '2e729d589fb3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table("trip_book",sa.Column("booking_id",sa.Integer,primary_key=True),
                                sa.Column("trip_id",sa.Integer,sa.ForeignKey("trip.trip_id"),nullable=False),
                                sa.Column("driver_id",sa.Integer,sa.ForeignKey("user.user_id"),nullable=False),
                                sa.Column("passenger_id",sa.Integer,sa.ForeignKey("user.user_id"),nullable=False,unique=True),
                                sa.Column("booking_status",sa.Enum(enums.BookingStatus),nullable=False,server_default=enums.BookingStatus.PENDING.value),
                                sa.Column("payable_amount",sa.Integer,nullable=False),
                                sa.Column("seat_count",sa.Integer,nullable=False),
                                sa.Column("booking_time",sa.TIMESTAMP(timezone=True),nullable=False,server_default=sa.text("now()"))
                    )
    pass


def downgrade() -> None:
    op.drop_table("trip_book")
    pass
