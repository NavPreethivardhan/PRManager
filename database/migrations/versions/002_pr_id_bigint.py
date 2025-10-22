"""Change github_pr_id to BIGINT

Revision ID: 002
Revises: 001
Create Date: 2025-10-16 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('pull_requests') as batch_op:
        batch_op.alter_column('github_pr_id', type_=sa.BigInteger())


def downgrade() -> None:
    with op.batch_alter_table('pull_requests') as batch_op:
        batch_op.alter_column('github_pr_id', type_=sa.Integer())}
