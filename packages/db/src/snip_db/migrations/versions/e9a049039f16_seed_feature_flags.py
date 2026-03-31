"""seed feature flags

Revision ID: e9a049039f16
Revises: cd8b49b33eee
Create Date: 2026-03-29 19:39:04.461167

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'e9a049039f16'
down_revision: Union[str, None] = 'cd8b49b33eee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO feature_flags (key, enabled, description, updated_at) VALUES
            ('custom_short_codes', false, 'Allow users to set custom short codes', NOW()),
            ('click_notifications', true, 'Send email when link hits click threshold', NOW()),
            ('analytics_dashboard', true, 'Show BigQuery analytics chart on dashboard', NOW())
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DELETE FROM feature_flags
        WHERE key IN ('custom_short_codes', 'click_notifications', 'analytics_dashboard')
        """
    )
