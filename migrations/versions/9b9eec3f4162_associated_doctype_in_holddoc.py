"""associated_doctype in Holddoc

Revision ID: 9b9eec3f4162
Revises: 109f847af121
Create Date: 2020-03-05 12:24:47.626387

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9b9eec3f4162'
down_revision = '109f847af121'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('holddoc', sa.Column('associated_doctype_name', sa.String(length=120), nullable=True))
    op.create_foreign_key(None, 'holddoc', 'doctype', ['associated_doctype_name'], ['name'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'holddoc', type_='foreignkey')
    op.drop_column('holddoc', 'associated_doctype_name')
    # ### end Alembic commands ###
