"""Initial metadata tables with db_schema

Revision ID: 2249d45d45c7
Revises: 
Create Date: 2025-02-11 20:46:07.587923

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2249d45d45c7'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('table_metadata', schema=None) as batch_op:
        batch_op.add_column(sa.Column('db_schema', sa.String(), nullable=True))
        batch_op.drop_column('schema')

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('table_metadata', schema=None) as batch_op:
        batch_op.add_column(sa.Column('schema', sa.VARCHAR(), autoincrement=False, nullable=True))
        batch_op.drop_column('db_schema')

    # ### end Alembic commands ###
