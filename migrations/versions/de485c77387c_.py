"""empty message

Revision ID: de485c77387c
Revises: d3d1df47908b
Create Date: 2023-05-11 14:53:54.826311

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'de485c77387c'
down_revision = 'd3d1df47908b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('participant_profile', sa.Column('experience', postgresql.ARRAY(sa.String()), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('participant_profile', 'experience')
    # ### end Alembic commands ###
