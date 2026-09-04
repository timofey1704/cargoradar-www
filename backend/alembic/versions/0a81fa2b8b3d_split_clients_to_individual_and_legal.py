"""split clients to individual and legal

Revision ID: 0a81fa2b8b3d
Revises: 48323bd411e0
Create Date: 2026-09-03 15:04:51.580901

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '0a81fa2b8b3d'
down_revision: Union[str, Sequence[str], None] = '48323bd411e0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Нативный PG-enum. create_type=False — тип создаём явно в upgrade()/downgrade(),
# иначе op.add_column падает с 'type "clienttypes" does not exist'.
clienttypes = postgresql.ENUM(
    'individual',
    'legal',
    name='clienttypes',
    create_type=False,
)


def upgrade() -> None:
    """Upgrade schema."""
    clienttypes.create(op.get_bind(), checkfirst=True)

    # Все существующие клиенты были «физическими лицами», поэтому подставляем
    # временный DEFAULT, а после добавления колонки снимаем его, чтобы схема
    # точно совпадала с моделью (серверный дефолт у типа клиента не предусмотрен).
    op.add_column(
        'clients',
        sa.Column(
            'type',
            clienttypes,
            nullable=False,
            server_default='individual',
        ),
    )
    op.alter_column('clients', 'type', server_default=None)

    # Таблица юридических лиц (не попала в autogenerate: модель LegalClient
    # была импортирована в client/models/__init__.py уже после генерации).
    op.create_table(
        'legal_clients',
        sa.Column('client_id', sa.Integer(), nullable=False),
        sa.Column('legal_name', sa.String(length=255), nullable=False),
        sa.Column('unp', sa.String(length=50), nullable=False),
        sa.Column('address', sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id']),
        sa.PrimaryKeyConstraint('client_id'),
        sa.UniqueConstraint('unp'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('legal_clients')
    op.drop_column('clients', 'type')
    clienttypes.drop(op.get_bind(), checkfirst=True)
