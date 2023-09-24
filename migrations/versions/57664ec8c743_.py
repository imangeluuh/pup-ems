"""empty message

Revision ID: 57664ec8c743
Revises: 66490fe22b01
Create Date: 2023-09-04 22:57:02.248037

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '57664ec8c743'
down_revision = '66490fe22b01'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Student', schema=None) as batch_op:
        batch_op.add_column(sa.Column('StudentId', sa.String(length=36), nullable=False))
        batch_op.drop_constraint('Student_VolunteerId_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'User', ['StudentId'], ['UserId'], ondelete='CASCADE')
        batch_op.drop_column('VolunteerId')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Student', schema=None) as batch_op:
        batch_op.add_column(sa.Column('VolunteerId', sa.VARCHAR(length=36), autoincrement=False, nullable=False))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('Student_VolunteerId_fkey', 'User', ['VolunteerId'], ['UserId'], ondelete='CASCADE')
        batch_op.drop_column('StudentId')

    # ### end Alembic commands ###
