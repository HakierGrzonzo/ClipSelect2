"""Add stream index column

Revision ID: 81d1de28179f
Revises: eeba81b893e3
Create Date: 2022-08-11 22:07:59.518777

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "81d1de28179f"
down_revision = "eeba81b893e3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "Episode",
        sa.Column("subtitle_track_index", sa.Integer(), nullable=False),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("Episode", "subtitle_track_index")
    # ### end Alembic commands ###
