"""add multiple_orgs feature flag

Revision ID: 085fc05d6b8e
Revises: e9a049039f16
Create Date: 2026-03-29 22:33:23.750617

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '085fc05d6b8e'
down_revision: Union[str, None] = 'e9a049039f16'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO feature_flags (key, enabled, description, updated_at) VALUES
            ('multiple_orgs', false, 'Allow users to create more than one organization', NOW())
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DELETE FROM feature_flags WHERE key = 'multiple_orgs'
        """
    )
