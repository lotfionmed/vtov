"""Add messaging and profile columns

Revision ID: 068f86d0d118
Revises: c8a1459e5b23
Create Date: 2024-12-09 23:37:57.645818

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '068f86d0d118'
down_revision = 'c8a1459e5b23'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('comment')
    op.drop_table('follower')
    op.drop_table('message')
    op.drop_table('post')
    op.drop_table('like')
    op.drop_table('user')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('username', sa.VARCHAR(length=80), nullable=False),
    sa.Column('email', sa.VARCHAR(length=120), nullable=False),
    sa.Column('password', sa.VARCHAR(length=120), nullable=False),
    sa.Column('bio', sa.VARCHAR(length=500), nullable=True),
    sa.Column('profile_pic', sa.VARCHAR(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('like',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.Column('post_id', sa.INTEGER(), nullable=False),
    sa.Column('timestamp', sa.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['post_id'], ['post.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('post',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('image_path', sa.VARCHAR(length=255), nullable=True),
    sa.Column('caption', sa.TEXT(), nullable=True),
    sa.Column('timestamp', sa.DATETIME(), nullable=True),
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('message',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('sender_id', sa.INTEGER(), nullable=False),
    sa.Column('receiver_id', sa.INTEGER(), nullable=False),
    sa.Column('content', sa.TEXT(), nullable=False),
    sa.Column('timestamp', sa.DATETIME(), nullable=True),
    sa.Column('is_read', sa.BOOLEAN(), nullable=True),
    sa.ForeignKeyConstraint(['receiver_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['sender_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('follower',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('follower_id', sa.INTEGER(), nullable=False),
    sa.Column('followed_id', sa.INTEGER(), nullable=False),
    sa.Column('timestamp', sa.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['followed_id'], ['user.id'], ),
    sa.ForeignKeyConstraint(['follower_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('comment',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('content', sa.TEXT(), nullable=False),
    sa.Column('timestamp', sa.DATETIME(), nullable=True),
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.Column('post_id', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['post_id'], ['post.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
