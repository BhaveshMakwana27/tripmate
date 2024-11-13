"""create payment table

Revision ID: 6458b28ac1c7
Revises: 4d8862d370e4
Create Date: 2024-11-09 12:58:20.820632

"""
from typing import Sequence, Union
from app import enums
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6458b28ac1c7'
down_revision: Union[str, None] = '4d8862d370e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table("payment",
                    sa.Column('payment_id',sa.Integer,primary_key=True),
                    sa.Column("booking_id",sa.Integer,sa.ForeignKey('trip_book.booking_id'),nullable=False),
                    sa.Column('amount',sa.Integer,nullable=False),
                    sa.Column('payment_method',sa.Enum(enums.PaymentMethod),nullable=False,server_default=enums.PaymentMethod.CASH.value),
                    sa.Column('payment_time',sa.TIMESTAMP(timezone=True),nullable=False,server_default=sa.text('now()')),
                    sa.Column('payment_status',sa.Enum(enums.PaymentStatus),nullable=False,server_default=enums.PaymentStatus.PENDING.value)
                    )
    pass


def downgrade() -> None:
    op.drop_table('payment')
    pass
