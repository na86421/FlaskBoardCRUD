"""empty message

Revision ID: 4dbcef5aa3e0
Revises: e3fdacbdb80a
Create Date: 2021-01-05 14:43:46.962564

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4dbcef5aa3e0'
down_revision = 'e3fdacbdb80a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('board_list',
    sa.Column('index', sa.Integer(), nullable=False),
    sa.Column('board_name', sa.String(), nullable=True),
    sa.Column('group', sa.Integer(), nullable=True),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('text', sa.String(), nullable=True),
    sa.Column('date', sa.TIMESTAMP(), nullable=True),
    sa.PrimaryKeyConstraint('index')
    )
    op.create_table('user',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    op.drop_table('board_list')
    # ### end Alembic commands ###