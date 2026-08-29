"""add staffing requirement skill and certification relationships

Revision ID: b0130b4aa235
Revises: ae7dc1607d02
Create Date: 2026-08-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b0130b4aa235"
down_revision: Union[str, Sequence[str], None] = "ae7dc1607d02"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # --------------------------------------------------------
    # Staffing requirement -> required skills
    # --------------------------------------------------------

    op.create_table(
        "staffing_requirement_skills",
        sa.Column(
            "staffing_requirement_skill_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "staffing_requirement_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "skill_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["staffing_requirement_id"],
            [
                "staffing_requirements.staffing_requirement_id"
            ],
        ),
        sa.ForeignKeyConstraint(
            ["skill_id"],
            ["skills.skill_id"],
        ),
        sa.PrimaryKeyConstraint(
            "staffing_requirement_skill_id"
        ),
        sa.UniqueConstraint(
            "staffing_requirement_id",
            "skill_id",
            name="uq_staffing_requirement_skill",
        ),
    )

    op.create_index(
        op.f(
            "ix_staffing_requirement_skills_staffing_requirement_id"
        ),
        "staffing_requirement_skills",
        ["staffing_requirement_id"],
        unique=False,
    )

    op.create_index(
        op.f(
            "ix_staffing_requirement_skills_skill_id"
        ),
        "staffing_requirement_skills",
        ["skill_id"],
        unique=False,
    )

    # --------------------------------------------------------
    # Staffing requirement -> required certifications
    # --------------------------------------------------------

    op.create_table(
        "staffing_requirement_certifications",
        sa.Column(
            "staffing_requirement_certification_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "staffing_requirement_id",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "certification_name",
            sa.String(length=150),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["staffing_requirement_id"],
            [
                "staffing_requirements.staffing_requirement_id"
            ],
        ),
        sa.PrimaryKeyConstraint(
            "staffing_requirement_certification_id"
        ),
        sa.UniqueConstraint(
            "staffing_requirement_id",
            "certification_name",
            name="uq_staffing_requirement_certification",
        ),
    )

    op.create_index(
        op.f(
            "ix_staffing_requirement_certifications_staffing_requirement_id"
        ),
        "staffing_requirement_certifications",
        ["staffing_requirement_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f(
            "ix_staffing_requirement_certifications_staffing_requirement_id"
        ),
        table_name="staffing_requirement_certifications",
    )

    op.drop_table(
        "staffing_requirement_certifications"
    )

    op.drop_index(
        op.f(
            "ix_staffing_requirement_skills_skill_id"
        ),
        table_name="staffing_requirement_skills",
    )

    op.drop_index(
        op.f(
            "ix_staffing_requirement_skills_staffing_requirement_id"
        ),
        table_name="staffing_requirement_skills",
    )

    op.drop_table(
        "staffing_requirement_skills"
    )