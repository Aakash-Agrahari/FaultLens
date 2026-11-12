from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

#upgrade creates the table
def upgrade() -> None:
    op.create_table(
        "incidents",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "title",
            sa.String(length=150),
            nullable=False
        ),
        sa.Column(
            "description",
            sa.String(length=2000),
            nullable=False
        ),
        sa.Column(
            "severity",
            sa.String(length=20),
            nullable=False
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False
        )
    )

def downgrade() -> None:
    op.drop_table("incidents")    
