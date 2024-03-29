"""roles to view audit in doctype

Revision ID: 6036e24e361d
Revises: 62fc268c2cf8
Create Date: 2020-03-01 10:57:09.341816

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '6036e24e361d'
down_revision = '62fc268c2cf8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('doctype', sa.Column('roles_to_view_audit', mysql.JSON(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('doctype', 'roles_to_view_audit')
    # ### end Alembic commands ###
