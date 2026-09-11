"""Phase 2A Device Registration & Live Management Migration

Revision ID: 001_phase2a_devices
Revises: 
Create Date: 2026-08-23 13:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001_phase2a_devices'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Ensure unique constraint and indexes on devices table
    try:
        op.create_index(op.f('ix_devices_device_uuid'), 'devices', ['device_uuid'], unique=True)
    except Exception:
        pass

    try:
        op.create_index(op.f('ix_devices_hostname'), 'devices', ['hostname'], unique=False)
    except Exception:
        pass

    try:
        op.create_index(op.f('ix_devices_status'), 'devices', ['status'], unique=False)
    except Exception:
        pass

    try:
        op.create_index(op.f('ix_devices_last_seen_at'), 'devices', ['last_seen_at'], unique=False)
    except Exception:
        pass

def downgrade():
    try:
        op.drop_index(op.f('ix_devices_last_seen_at'), table_name='devices')
        op.drop_index(op.f('ix_devices_status'), table_name='devices')
        op.drop_index(op.f('ix_devices_hostname'), table_name='devices')
        op.drop_index(op.f('ix_devices_device_uuid'), table_name='devices')
    except Exception:
        pass
