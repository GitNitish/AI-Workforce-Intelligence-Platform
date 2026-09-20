from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.entities import (
    Project,
    Skill,
    StaffingRequirement,
    StaffingRequirementCertification,
    StaffingRequirementSkill,
)
from app.schemas.staffing_requirement import (
    StaffingRequirementCreate,
    StaffingRequirementUpdate,
)


def get_project(
    db: Session,
    project_id: str,
) -> Project | None:
    return db.get(Project, project_id)


def get_staffing_requirements(
    db: Session,
    project_id: str,
) -> list[StaffingRequirement]:
    statement = (
        select(StaffingRequirement)
        .where(
            StaffingRequirement.project_id == project_id
        )
        .order_by(
            StaffingRequirement.created_at.desc()
        )
    )

    return list(db.scalars(statement).all())


def get_staffing_requirement(
    db: Session,
    staffing_requirement_id: str,
) -> StaffingRequirement | None:
    statement = select(StaffingRequirement).where(
        StaffingRequirement.staffing_requirement_id
        == staffing_requirement_id
    )

    return db.scalar(statement)


def _set_required_skills(
    db: Session,
    requirement: StaffingRequirement,
    skill_ids: list[str],
) -> None:
    unique_skill_ids = list(dict.fromkeys(skill_ids))

    if unique_skill_ids:
        skills = list(
            db.scalars(
                select(Skill).where(
                    Skill.skill_id.in_(unique_skill_ids)
                )
            ).all()
        )

        found_skill_ids = {
            skill.skill_id
            for skill in skills
        }

        missing_skill_ids = [
            skill_id
            for skill_id in unique_skill_ids
            if skill_id not in found_skill_ids
        ]

        if missing_skill_ids:
            raise ValueError(
                "Skill not found: "
                + ", ".join(missing_skill_ids)
            )

    if requirement.staffing_requirement_id:
        db.execute(
            delete(StaffingRequirementSkill).where(
                StaffingRequirementSkill.staffing_requirement_id
                == requirement.staffing_requirement_id
            )
        )
        db.flush()

    requirement.required_skills = [
        StaffingRequirementSkill(
            skill_id=skill_id
        )
        for skill_id in unique_skill_ids
    ]


def _set_required_certifications(
    db: Session,
    requirement: StaffingRequirement,
    certification_names: list[str],
) -> None:
    unique_certification_names = list(
        dict.fromkeys(certification_names)
    )

    if requirement.staffing_requirement_id:
        db.execute(
            delete(StaffingRequirementCertification).where(
                StaffingRequirementCertification.staffing_requirement_id
                == requirement.staffing_requirement_id
            )
        )
        db.flush()

    requirement.required_certifications = [
        StaffingRequirementCertification(
            certification_name=certification_name
        )
        for certification_name in unique_certification_names
    ]


def create_staffing_requirement(
    db: Session,
    project_id: str,
    requirement_data: StaffingRequirementCreate,
) -> StaffingRequirement:
    project = get_project(db, project_id)

    if project is None:
        raise ValueError("Project not found")

    requirement = StaffingRequirement(
        project_id=project_id,
        role_name=requirement_data.role_name,
        required_quantity=requirement_data.required_quantity,
        required_experience=requirement_data.required_experience,
        required_proficiency=(
            requirement_data.required_proficiency
        ),
        start_date=requirement_data.start_date,
        end_date=requirement_data.end_date,
        priority=requirement_data.priority,
        status=requirement_data.status,
    )

    _set_required_skills(
        db,
        requirement,
        requirement_data.required_skill_ids,
    )

    _set_required_certifications(
        db,
        requirement,
        requirement_data.required_certifications,
    )

    db.add(requirement)
    db.commit()
    db.refresh(requirement)

    return requirement


def update_staffing_requirement(
    db: Session,
    staffing_requirement_id: str,
    requirement_data: StaffingRequirementUpdate,
) -> StaffingRequirement:
    requirement = get_staffing_requirement(
        db,
        staffing_requirement_id,
    )

    if requirement is None:
        raise ValueError("Staffing requirement not found")

    update_data = requirement_data.model_dump(
        exclude_unset=True
    )

    new_start_date = update_data.get(
        "start_date",
        requirement.start_date,
    )

    new_end_date = update_data.get(
        "end_date",
        requirement.end_date,
    )

    if (
        new_start_date is not None
        and new_end_date is not None
        and new_end_date < new_start_date
    ):
        raise ValueError(
            "end_date must be greater than "
            "or equal to start_date"
        )

    required_skill_ids = update_data.pop(
        "required_skill_ids",
        None,
    )

    required_certifications = update_data.pop(
        "required_certifications",
        None,
    )

    for field, value in update_data.items():
        setattr(
            requirement,
            field,
            value,
        )

    if required_skill_ids is not None:
        _set_required_skills(
            db,
            requirement,
            required_skill_ids,
        )

    if required_certifications is not None:
        _set_required_certifications(
            db,
            requirement,
            required_certifications,
        )

    db.commit()
    db.refresh(requirement)

    return requirement