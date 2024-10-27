"""create user table

Revision ID: d935ed25877b
Revises: 
Create Date: 2024-08-10 20:53:30.853776

"""
from typing import Sequence, Union
from app.config import settings
from app import enums
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd935ed25877b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('user',sa.Column('user_id',sa.Integer,primary_key=True),
                            sa.Column('name',sa.String,nullable=False),
                            sa.Column('email',sa.String,nullable=False,unique=True),
                            sa.Column('contact_no',sa.String,nullable=False,unique=True),
                            sa.Column('address_line',sa.String,nullable=False),
                            sa.Column('city',sa.String,nullable=False),
                            sa.Column('state',sa.String,nullable=False),
                            sa.Column('country',sa.String,nullable=False),
                            sa.Column('pincode',sa.Integer,nullable=False),
                            sa.Column('gender',sa.Enum(enums.Gender),nullable=False),
                            sa.Column('password',sa.String,nullable=False),
                            sa.Column('profile_photo',sa.String,nullable=False,server_default=settings.default_profile_photo_path),
                            sa.Column('ratings',sa.Double,nullable=False,server_default='0.0'),
                            sa.Column('created_at',sa.TIMESTAMP(timezone=True),server_default=sa.text('now()'),nullable=False),
                            sa.Column('updated_at',sa.TIMESTAMP(timezone=True),server_default=sa.text('now()'),nullable=False)
                        )
    pass


def downgrade() -> None:
    op.drop_table('user')
    pass
