"""updated tables

Revision ID: b7029b866682
Revises: cdd820d0d0f0
Create Date: 2023-06-26 12:35:01.384620

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b7029b866682'
down_revision = 'cdd820d0d0f0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('addresses', schema=None) as batch_op:
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               type_=sa.String(length=36),
               existing_nullable=True)

    with op.batch_alter_table('therapists', schema=None) as batch_op:
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               type_=sa.String(length=36),
               existing_nullable=True)

    with op.batch_alter_table('user_appointment', schema=None) as batch_op:
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               type_=sa.String(length=36),
               existing_nullable=True)

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('user_id',
               existing_type=sa.VARCHAR(length=32),
               type_=sa.String(length=36),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('user_id',
               existing_type=sa.String(length=36),
               type_=sa.VARCHAR(length=32),
               existing_nullable=False)

    with op.batch_alter_table('user_appointment', schema=None) as batch_op:
        batch_op.alter_column('user_id',
               existing_type=sa.String(length=36),
               type_=sa.INTEGER(),
               existing_nullable=True)

    with op.batch_alter_table('therapists', schema=None) as batch_op:
        batch_op.alter_column('user_id',
               existing_type=sa.String(length=36),
               type_=sa.INTEGER(),
               existing_nullable=True)

    with op.batch_alter_table('addresses', schema=None) as batch_op:
        batch_op.alter_column('user_id',
               existing_type=sa.String(length=36),
               type_=sa.INTEGER(),
               existing_nullable=True)

    # ### end Alembic commands ###
