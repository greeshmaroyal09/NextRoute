"""add missing indexes

Revision ID: add_missing_indexes_1
Revises: 
Create Date: 2026-08-05 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_missing_indexes_1'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Train stops
    op.create_index('ix_train_stops_station_id', 'train_stops', ['station_id'], unique=False)
    # Bus stop sequence
    op.create_index('ix_bus_stops_sequence_bus_stop_id', 'bus_stops_sequence', ['bus_stop_id'], unique=False)
    # Nearby connections
    op.create_index('ix_nearby_connections_station_id', 'nearby_connections', ['station_id'], unique=False)
    op.create_index('ix_nearby_connections_bus_stop_id', 'nearby_connections', ['bus_stop_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_nearby_connections_bus_stop_id', table_name='nearby_connections')
    op.drop_index('ix_nearby_connections_station_id', table_name='nearby_connections')
    op.drop_index('ix_bus_stops_sequence_bus_stop_id', table_name='bus_stops_sequence')
    op.drop_index('ix_train_stops_station_id', table_name='train_stops')
