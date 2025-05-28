"""add PROMOCODE level to UserSubscriptionLevels enum

Revision ID: 2a209b5da9a6
Revises: 1fcb8c9962f0
Create Date: 2025-05-23 19:52:12.463160

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "baeafb64d7f7"
down_revision: Union[str, None] = "1fcb8c9962f0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute("ALTER TYPE usersubscriptionlevels ADD VALUE IF NOT EXISTS 'PROMOCODE'")


def downgrade():
    pass
