"""Add StartDate to Project Model"

Revision ID: e39ca1f270a8
Revises: 06f86b1af5f6
Create Date: 2023-08-27 10:43:58.374615

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e39ca1f270a8'
down_revision = '06f86b1af5f6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Project', schema=None) as batch_op:
        batch_op.add_column(sa.Column('StartDate', sa.Date(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Project', schema=None) as batch_op:
        batch_op.drop_column('StartDate')

    # ### end Alembic commands ###
