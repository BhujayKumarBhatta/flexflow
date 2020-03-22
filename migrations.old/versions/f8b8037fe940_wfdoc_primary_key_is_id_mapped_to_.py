"""wfdoc primary key is id mapped to primval_docdata

Revision ID: f8b8037fe940
Revises: e77ddac5cb0f
Create Date: 2020-02-19 11:53:19.685245

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'f8b8037fe940'
down_revision = 'e77ddac5cb0f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('wfdoc', sa.Column('id', sa.String(length=500), nullable=False))
    op.drop_index('primvalue_of_docdata', table_name='wfdoc')
    op.create_unique_constraint(None, 'wfdoc', ['id'])
    op.drop_column('wfdoc', 'primvalue_of_docdata')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('wfdoc', sa.Column('primvalue_of_docdata', mysql.VARCHAR(length=500), nullable=False))
    op.drop_constraint(None, 'wfdoc', type_='unique')
    op.create_index('primvalue_of_docdata', 'wfdoc', ['primvalue_of_docdata'], unique=True)
    op.drop_column('wfdoc', 'id')
    # ### end Alembic commands ###