"""updated tables

Revision ID: 9116f70715e1
Revises: b7029b866682
Create Date: 2023-06-26 15:46:56.403692

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9116f70715e1'
down_revision = 'b7029b866682'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('appointments', schema=None) as batch_op:
        batch_op.alter_column('appointment_date',
               existing_type=sa.DATE(),
               type_=sa.String(),
               existing_nullable=False)
        batch_op.drop_column('end_datetime')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('appointments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('end_datetime', sa.DATE(), nullable=False))
        batch_op.alter_column('appointment_date',
               existing_type=sa.String(),
               type_=sa.DATE(),
               existing_nullable=False)

    # ### end Alembic commands ###