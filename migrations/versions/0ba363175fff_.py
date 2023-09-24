"""empty message

Revision ID: 0ba363175fff
Revises: 4fe85abc5139
Create Date: 2023-09-07 14:15:28.731716

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0ba363175fff'
down_revision = '4fe85abc5139'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Announcement', schema=None) as batch_op:
        batch_op.add_column(sa.Column('ProjectId', sa.Integer(), nullable=False))
        batch_op.drop_constraint('Announcement_ExtensionProgramId_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'Project', ['ProjectId'], ['ProjectId'], ondelete='CASCADE')
        batch_op.drop_column('ExtensionProgramId')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Announcement', schema=None) as batch_op:
        batch_op.add_column(sa.Column('ExtensionProgramId', sa.INTEGER(), autoincrement=False, nullable=False))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('Announcement_ExtensionProgramId_fkey', 'ExtensionProgram', ['ExtensionProgramId'], ['ExtensionProgramId'], ondelete='CASCADE')
        batch_op.drop_column('ProjectId')

    # ### end Alembic commands ###
