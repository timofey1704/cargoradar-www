"""Move vehicle photos into a separate table.

Revision ID: f8a3c2d1e6b9
Revises: 91937c209f1a
Create Date: 2026-10-14
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f8a3c2d1e6b9"
down_revision: Union[str, Sequence[str], None] = "91937c209f1a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "vehicle_photos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("vehicle_id", sa.Integer(), nullable=False),
        sa.Column("image", sa.String(length=255), nullable=False),
        sa.Column("position", sa.Integer(), server_default="0", nullable=False),
        sa.ForeignKeyConstraint(["vehicle_id"], ["vehicles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_vehicle_photos_vehicle_id"), "vehicle_photos", ["vehicle_id"])
    op.execute(
        "INSERT INTO vehicle_photos (vehicle_id, image, position) "
        "SELECT id, photo_url, 0 FROM vehicles WHERE photo_url IS NOT NULL"
    )
    op.drop_column("vehicles", "photo_url")


def downgrade() -> None:
    op.add_column("vehicles", sa.Column("photo_url", sa.String(length=255), nullable=True))
    op.execute(
        "UPDATE vehicles SET photo_url = ("
        "SELECT image FROM vehicle_photos "
        "WHERE vehicle_photos.vehicle_id = vehicles.id "
        "ORDER BY position, id LIMIT 1"
        ")"
    )
    op.drop_index(op.f("ix_vehicle_photos_vehicle_id"), table_name="vehicle_photos")
    op.drop_table("vehicle_photos")