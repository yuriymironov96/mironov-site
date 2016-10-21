"""empty message

Revision ID: c2793a312889
Revises: 828709644580
Create Date: 2016-10-14 16:42:11.655889

"""

# revision identifiers, used by Alembic.
revision = 'c2793a312889'
down_revision = '828709644580'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(u'tag-post_tag_id_fkey', 'tag-post', type_='foreignkey')
    op.create_foreign_key(None, 'tag-post', 'tags', ['tag_id'], ['id'], ondelete='CASCADE')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'tag-post', type_='foreignkey')
    op.create_foreign_key(u'tag-post_tag_id_fkey', 'tag-post', 'tags', ['tag_id'], ['id'])
    ### end Alembic commands ###