"""empty message

Revision ID: 54a6ac946516
Revises: 
Create Date: 2023-03-14 15:56:27.451975

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '54a6ac946516'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('mar1',
    sa.Column('marital_status_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('status', sa.String(length=25), nullable=True),
    sa.Column('yes_bank_text', sa.String(length=10), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('sorting_order', sa.Integer(), nullable=True),
    sa.Column('default_list', sa.Boolean(), nullable=True),
    sa.Column('system_text', sa.String(length=100), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('marital_status_id')
    )
    op.create_table('mar2',
    sa.Column('marital_status_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('status', sa.String(length=25), nullable=True),
    sa.Column('yes_bank_text', sa.String(length=10), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('sorting_order', sa.Integer(), nullable=True),
    sa.Column('default_list', sa.Boolean(), nullable=True),
    sa.Column('system_text', sa.String(length=100), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('marital_status_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('mar2')
    op.drop_table('mar1')
    # ### end Alembic commands ###
