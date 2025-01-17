"""empty message

Revision ID: 4e9e93de09c3
Revises: 5590025e0cd1
Create Date: 2021-05-13 20:02:41.011881

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4e9e93de09c3'
down_revision = '5590025e0cd1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Shows', 'Venue_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('Shows', 'Artist_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Shows', 'Artist_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('Shows', 'Venue_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###
