"""add total bounty amount

Revision ID: c2a262fda8d4
Revises: 5ca8346d7f19
Create Date: 2020-07-09 21:55:15.264122

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c2a262fda8d4'
down_revision = '5ca8346d7f19'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('pull_requests', sa.Column('total_bounty_amount', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('pull_requests', 'total_bounty_amount')
    # ### end Alembic commands ###
