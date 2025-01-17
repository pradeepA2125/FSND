"""empty message

Revision ID: da4cf49155e3
Revises: f43531d042f1
Create Date: 2021-05-12 23:36:16.015004

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'da4cf49155e3'
down_revision = 'f43531d042f1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Shows',
    sa.Column('Venue_id', sa.Integer(), nullable=True),
    sa.Column('Artist_id', sa.Integer(), nullable=True),
    sa.Column('start_time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['Artist_id'], ['Artist.id'], ),
    sa.ForeignKeyConstraint(['Venue_id'], ['Venue.id'], )
    )
    op.add_column('Artist', sa.Column('venue_required', sa.Boolean(), nullable=False))
    op.add_column('Artist', sa.Column('seeking_description', sa.String(length=300), nullable=True))
    op.add_column('Venue', sa.Column('genres', sa.ARRAY(sa.String()), nullable=False))
    op.add_column('Venue', sa.Column('talent_required', sa.Boolean(), nullable=False))
    op.add_column('Venue', sa.Column('seeking_description', sa.String(length=300), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'seeking_description')
    op.drop_column('Venue', 'talent_required')
    op.drop_column('Venue', 'genres')
    op.drop_column('Artist', 'seeking_description')
    op.drop_column('Artist', 'venue_required')
    op.drop_table('Shows')
    # ### end Alembic commands ###
