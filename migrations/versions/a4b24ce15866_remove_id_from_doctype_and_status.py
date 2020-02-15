"""remove_id_from_doctype_and_status

Revision ID: a4b24ce15866
Revises: 
Create Date: 2020-02-15 15:01:11.653179

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'a4b24ce15866'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('doctype',
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.PrimaryKeyConstraint('name'),
    sa.UniqueConstraint('name')
    )
    op.create_table('wfstatus',
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.PrimaryKeyConstraint('name'),
    sa.UniqueConstraint('name')
    )
    op.create_table('wfaction',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('assocated_doctype_name', sa.String(length=120), nullable=True),
    sa.Column('need_prev_status', sa.String(length=120), nullable=False),
    sa.Column('need_current_status', sa.String(length=120), nullable=False),
    sa.Column('leads_to_status', sa.String(length=120), nullable=False),
    sa.Column('permitted_to_roles', mysql.JSON(), nullable=True),
    sa.ForeignKeyConstraint(['assocated_doctype_name'], ['doctype.name'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('wfaction')
    op.drop_table('wfstatus')
    op.drop_table('doctype')
    # ### end Alembic commands ###
