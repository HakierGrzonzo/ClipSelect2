"""Make relations not nullable

Revision ID: 0ed644dace18
Revises: 5b5e1881c0ae
Create Date: 2022-08-09 00:04:14.439499

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0ed644dace18"
down_revision = "5b5e1881c0ae"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "Caption", "episode_id", existing_type=postgresql.UUID(), nullable=False
    )
    op.alter_column(
        "Episode",
        "subseries_id",
        existing_type=postgresql.UUID(),
        nullable=False,
    )
    op.alter_column(
        "SubSeries",
        "series_id",
        existing_type=postgresql.UUID(),
        nullable=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "SubSeries", "series_id", existing_type=postgresql.UUID(), nullable=True
    )
    op.alter_column(
        "Episode",
        "subseries_id",
        existing_type=postgresql.UUID(),
        nullable=True,
    )
    op.alter_column(
        "Caption", "episode_id", existing_type=postgresql.UUID(), nullable=True
    )
    # ### end Alembic commands ###