"""updated therapist model, added Schedule table

Revision ID: d1388a59d26e
Revises: 37c14fca5cfe
Create Date: 2023-06-26 18:52:16.839687

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd1388a59d26e'
down_revision = '37c14fca5cfe'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('schedules',
    sa.Column('schedule_id', sa.Integer(), nullable=False),
    sa.Column('therapist_id', sa.Integer(), nullable=True),
    sa.Column('day_of_week', sa.String(length=10), nullable=False),
    sa.Column('start_time', sa.String(), nullable=False),
    sa.Column('end_time', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['therapist_id'], ['therapists.therapist_id'], name=op.f('fk_schedules_therapist_id_therapists')),
    sa.PrimaryKeyConstraint('schedule_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('schedules')
    # ### end Alembic commands ###
