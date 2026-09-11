from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.entities import (
    Employee,
    EmployeeSkill,
    StaffingRequirement,
)


def discover_candidate_employees(
    db: Session,
    staffing_requirement: StaffingRequirement,
) -> list[Employee]:
    """
    Discover the initial candidate pool for a staffing requirement.

    Candidate discovery is intentionally narrower than eligibility.

    Discovery rules:
    - Only active employees are considered.
    - If required skills exist, an employee must possess all of them.
    - If no required skills exist, all active employees are considered.
    - Results are returned deterministically by employee name and ID.

    Mandatory eligibility checks such as proficiency, experience,
    certifications, availability, and requirement-period capacity
    remain the responsibility of the existing eligibility engine.
    """

    required_skill_ids = {
        required_skill.skill_id
        for required_skill in staffing_requirement.required_skills
    }

    # --------------------------------------------------------
    # No skill requirement:
    # all active employees form the initial candidate pool.
    # --------------------------------------------------------

    if not required_skill_ids:
        statement = (
            select(Employee)
            .where(
                Employee.status == "active"
            )
            .order_by(
                Employee.name.asc(),
                Employee.employee_id.asc(),
            )
        )

        return list(
            db.scalars(statement).all()
        )

    # --------------------------------------------------------
    # Skill-based candidate discovery:
    # identify active employees possessing every required skill.
    # --------------------------------------------------------

    statement = (
        select(Employee)
        .join(
            EmployeeSkill,
            EmployeeSkill.employee_id
            == Employee.employee_id,
        )
        .where(
            Employee.status == "active",
            EmployeeSkill.skill_id.in_(
                required_skill_ids
            ),
        )
        .group_by(
            Employee.employee_id,
        )
        .having(
            func.count(
                func.distinct(EmployeeSkill.skill_id)
            )
            == len(required_skill_ids)
        )
        .order_by(
            Employee.name.asc(),
            Employee.employee_id.asc(),
        )
    )

    return list(
        db.scalars(statement).all()
    )