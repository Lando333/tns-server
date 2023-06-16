"""empty message

Revision ID: eae3ed671aba
Revises: 213f2ddf3afc
Create Date: 2023-06-15 11:29:14.964148

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eae3ed671aba'
down_revision = '213f2ddf3afc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('therapist_service_association')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('therapist_service_association',
    sa.Column('therapist_id', sa.INTEGER(), nullable=True),
    sa.Column('service_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['service_id'], ['services.service_id'], name='fk_therapist_service_association_service_id_services'),
    sa.ForeignKeyConstraint(['therapist_id'], ['therapists.therapist_id'], name='fk_therapist_service_association_therapist_id_therapists')
    )
    # ### end Alembic commands ###
