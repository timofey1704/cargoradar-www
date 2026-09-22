"""add routes table with postgis coordinates

Revision ID: 27b9985ef5e7
Revises: 4898449e69c2
Create Date: 2026-09-21 21:30:27.902618

"""
from typing import Sequence, Union

from alembic import op
import geoalchemy2
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '27b9985ef5e7'
down_revision: Union[str, Sequence[str], None] = '4898449e69c2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # В образе postgis/postgis расширение уже включено, но IF NOT EXISTS делает
    # миграцию применимой и на чистом postgres.
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    op.create_table(
        'routes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('executor_id', sa.Integer(), nullable=False),
        sa.Column('point_a', sa.String(length=255), nullable=False),
        sa.Column('point_b', sa.String(length=255), nullable=False),
        # Координаты точек маршрута в WGS84 (EPSG:4326), порядок lng/lat.
        # spatial_index=False, потому что GiST-индексы создаём ниже явно:
        # иначе GeoAlchemy2 создаст их сам во время create_table и имена совпадут.
        sa.Column(
            'point_a_location',
            geoalchemy2.types.Geometry(geometry_type='POINT', srid=4326, spatial_index=False),
            nullable=False,
        ),
        sa.Column(
            'point_b_location',
            geoalchemy2.types.Geometry(geometry_type='POINT', srid=4326, spatial_index=False),
            nullable=False,
        ),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('price', sa.Float(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['executor_id'], ['executors.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_routes_executor_id'), 'routes', ['executor_id'], unique=False)
    # GiST-индексы под пространственные запросы (ST_DWithin/ST_Distance/&&).
    # Имена повторяют схему GeoAlchemy2 (idx_<table>_<column>), чтобы
    # autogenerate не видел расхождений с моделью.
    op.create_index(
        'idx_routes_point_a_location',
        'routes',
        ['point_a_location'],
        unique=False,
        postgresql_using='gist',
    )
    op.create_index(
        'idx_routes_point_b_location',
        'routes',
        ['point_b_location'],
        unique=False,
        postgresql_using='gist',
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('idx_routes_point_b_location', table_name='routes')
    op.drop_index('idx_routes_point_a_location', table_name='routes')
    op.drop_index(op.f('ix_routes_executor_id'), table_name='routes')
    op.drop_table('routes')
