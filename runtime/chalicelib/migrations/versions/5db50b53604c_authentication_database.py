"""Authentication Database

Revision ID: 5db50b53604c
Revises: 
Create Date: 2023-02-28 14:52:27.476871

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5db50b53604c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('question', sa.String(), nullable=True))
    op.add_column('users', sa.Column('answer', sa.String(), nullable=True))
    op.add_column('users', sa.Column('reset_code', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'reset_code')
    op.drop_column('users', 'answer')
    op.drop_column('users', 'question')
    # ### end Alembic commands ###
