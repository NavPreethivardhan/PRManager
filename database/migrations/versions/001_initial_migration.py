"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create pull_requests table
    op.create_table('pull_requests',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('github_pr_id', sa.Integer(), nullable=True),
    sa.Column('repository_full_name', sa.String(), nullable=True),
    sa.Column('pr_number', sa.Integer(), nullable=True),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('author', sa.String(), nullable=True),
    sa.Column('state', sa.String(), nullable=True),
    sa.Column('classification', sa.String(), nullable=True),
    sa.Column('confidence', sa.Float(), nullable=True),
    sa.Column('priority_score', sa.Integer(), nullable=True),
    sa.Column('reasoning', sa.Text(), nullable=True),
    sa.Column('suggested_action', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('analyzed_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_pull_requests_id'), 'pull_requests', ['id'], unique=False)
    op.create_index(op.f('ix_pull_requests_github_pr_id'), 'pull_requests', ['github_pr_id'], unique=True)
    op.create_index(op.f('ix_pull_requests_repository_full_name'), 'pull_requests', ['repository_full_name'], unique=False)
    op.create_index(op.f('ix_pull_requests_pr_number'), 'pull_requests', ['pr_number'], unique=False)
    op.create_index(op.f('ix_pull_requests_author'), 'pull_requests', ['author'], unique=False)
    
    # Create repositories table
    op.create_table('repositories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('full_name', sa.String(), nullable=True),
    sa.Column('github_repo_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('owner', sa.String(), nullable=True),
    sa.Column('private', sa.Boolean(), nullable=True),
    sa.Column('language', sa.String(), nullable=True),
    sa.Column('auto_analyze_enabled', sa.Boolean(), nullable=True),
    sa.Column('webhook_installed', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_repositories_id'), 'repositories', ['id'], unique=False)
    op.create_index(op.f('ix_repositories_full_name'), 'repositories', ['full_name'], unique=True)
    op.create_index(op.f('ix_repositories_github_repo_id'), 'repositories', ['github_repo_id'], unique=True)
    op.create_index(op.f('ix_repositories_owner'), 'repositories', ['owner'], unique=False)
    
    # Create users table
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('github_user_id', sa.Integer(), nullable=True),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('avatar_url', sa.String(), nullable=True),
    sa.Column('api_key_encrypted', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_github_user_id'), 'users', ['github_user_id'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_github_user_id'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_repositories_owner'), table_name='repositories')
    op.drop_index(op.f('ix_repositories_github_repo_id'), table_name='repositories')
    op.drop_index(op.f('ix_repositories_full_name'), table_name='repositories')
    op.drop_index(op.f('ix_repositories_id'), table_name='repositories')
    op.drop_table('repositories')
    op.drop_index(op.f('ix_pull_requests_author'), table_name='pull_requests')
    op.drop_index(op.f('ix_pull_requests_pr_number'), table_name='pull_requests')
    op.drop_index(op.f('ix_pull_requests_repository_full_name'), table_name='pull_requests')
    op.drop_index(op.f('ix_pull_requests_github_pr_id'), table_name='pull_requests')
    op.drop_index(op.f('ix_pull_requests_id'), table_name='pull_requests')
    op.drop_table('pull_requests')
