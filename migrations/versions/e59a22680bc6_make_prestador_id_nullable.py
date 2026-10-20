"""make prestador_id nullable

Revision ID: e59a22680bc6
Revises: 328a5b8e4e79
Create Date: 2026-10-14 12:33:50.276474

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e59a22680bc6'
down_revision = '328a5b8e4e79'
branch_labels = None
depends_on = None


def upgrade():
    # The column already exists and is nullable, no changes needed
    pass


def downgrade():
    # No changes needed for downgrade
    pass