"""undo_rev_hide in action

Revision ID: c6d375b8d76b
Revises: 9b9eec3f4162
Create Date: 2020-03-06 09:36:47.083470

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'c6d375b8d76b'
down_revision = '9b9eec3f4162'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('wfaction', sa.Column('undo_prev_hide_for', mysql.JSON(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('wfaction', 'undo_prev_hide_for')
    # ### end Alembic commands ###
