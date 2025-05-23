"""Remove unique constraint in User.household_code

Revision ID: 1066f0edda30
Revises: 8287e13451af
Create Date: 2025-05-17 13:21:51.574692

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1066f0edda30'
down_revision = '8287e13451af'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint('uq_users_household_code', type_='unique')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_unique_constraint('uq_users_household_code', ['household_code'])

    # ### end Alembic commands ###
