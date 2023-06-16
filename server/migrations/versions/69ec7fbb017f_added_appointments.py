"""added appointments

Revision ID: 69ec7fbb017f
Revises: 6cd5fa01711d
Create Date: 2023-06-15 16:04:06.925767

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '69ec7fbb017f'
down_revision = '6cd5fa01711d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('appointments',
    sa.Column('appointment_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('therapist_id', sa.Integer(), nullable=True),
    sa.Column('appointment_date', sa.Date(), nullable=True),
    sa.Column('appointment_time', sa.Time(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['therapist_id'], ['therapists.therapist_id'], name=op.f('fk_appointments_therapist_id_therapists')),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], name=op.f('fk_appointments_user_id_users')),
    sa.PrimaryKeyConstraint('appointment_id')
    )
    op.create_table('user_appointment',
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('appointment_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['appointment_id'], ['appointments.appointment_id'], name=op.f('fk_user_appointment_appointment_id_appointments')),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], name=op.f('fk_user_appointment_user_id_users'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_appointment')
    op.drop_table('appointments')
    # ### end Alembic commands ###
