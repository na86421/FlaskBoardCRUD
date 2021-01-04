"""empty message

Revision ID: e8ddc319b0a4
Revises: 46297ca66eaa
Create Date: 2021-01-03 23:30:50.986355

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e8ddc319b0a4'
down_revision = '46297ca66eaa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('board_list',
    sa.Column('index', sa.Integer(), nullable=False),
    sa.Column('board_name', sa.String(), nullable=True),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('text', sa.String(), nullable=True),
    sa.Column('date', sa.TIMESTAMP(), nullable=True),
    sa.PrimaryKeyConstraint('index')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('board_list')
    # ### end Alembic commands ###
