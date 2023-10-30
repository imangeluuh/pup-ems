"""Add speaker model

Revision ID: 66f9ca6c5f66
Revises: fd3a22b8b13b
Create Date: 2023-10-30 14:54:46.261379

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '66f9ca6c5f66'
down_revision = 'fd3a22b8b13b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Speaker',
    sa.Column('SpeakerId', sa.Integer(), nullable=False),
    sa.Column('FirstName', sa.String(length=50), nullable=False),
    sa.Column('MiddleName', sa.String(length=50), nullable=True),
    sa.Column('LastName', sa.String(length=50), nullable=False),
    sa.Column('ContactDetails', sa.String(length=13), nullable=False),
    sa.PrimaryKeyConstraint('SpeakerId')
    )
    with op.batch_alter_table('Activity', schema=None) as batch_op:
        batch_op.add_column(sa.Column('SpeakerId', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(None, 'Speaker', ['SpeakerId'], ['SpeakerId'], ondelete='CASCADE')

    with op.batch_alter_table('Response', schema=None) as batch_op:
        batch_op.drop_constraint('Response_SurveyId_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'Survey', ['SurveyId'], ['SurveyId'], ondelete='CASCADE')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('Response', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('Response_SurveyId_fkey', 'Survey', ['SurveyId'], ['SurveyId'])

    with op.batch_alter_table('Activity', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('SpeakerId')

    op.drop_table('Speaker')
    # ### end Alembic commands ###
