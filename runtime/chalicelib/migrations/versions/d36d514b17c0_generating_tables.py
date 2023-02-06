"""generating_Tables>

Revision ID: d36d514b17c0
Revises: 
Create Date: 2023-02-06 20:21:54.177234

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd36d514b17c0'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('market_day',
    sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('day', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=10), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('sectors',
    sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('description', sa.String(length=200), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('email', sa.String(length=50), nullable=False),
    sa.Column('password', sa.String(length=50), nullable=False),
    sa.Column('available_funds', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('blocked_funds', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('stocks',
    sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=20), nullable=False),
    sa.Column('total_volume', sa.Integer(), nullable=False),
    sa.Column('unallocated', sa.Integer(), nullable=False),
    sa.Column('price', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('sectors_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['sectors_id'], ['sectors.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('holdings',
    sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('volume', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('bid_price', sa.String(length=4), nullable=False),
    sa.Column('bought_on', sa.Date(), nullable=False),
    sa.Column('stocks_id', sa.Integer(), nullable=True),
    sa.Column('users_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['stocks_id'], ['stocks.id'], ),
    sa.ForeignKeyConstraint(['users_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ohlcv',
    sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), nullable=False),
    sa.Column('open', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('high', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('low', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('close', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('volume', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('market_id', sa.Integer(), nullable=True),
    sa.Column('stocks_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['market_id'], ['market_day.id'], ),
    sa.ForeignKeyConstraint(['stocks_id'], ['stocks.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('orders',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('bid_price', sa.Numeric(precision=12, scale=2), nullable=False),
    sa.Column('type', sa.String(length=4), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=False),
    sa.Column('bid_volume', sa.Integer(), nullable=False),
    sa.Column('executed_volume', sa.Integer(), nullable=False),
    sa.Column('stocks_id', sa.Integer(), nullable=True),
    sa.Column('users_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['stocks_id'], ['stocks.id'], ),
    sa.ForeignKeyConstraint(['users_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('orders')
    op.drop_table('ohlcv')
    op.drop_table('holdings')
    op.drop_table('stocks')
    op.drop_table('users')
    op.drop_table('sectors')
    op.drop_table('market_day')
    # ### end Alembic commands ###