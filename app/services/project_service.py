from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.entities import Allocation, Employee, Project
from app.schemas.project import ProjectCreate, ProjectUpdate


def get_projects(db: Session) -> list[Project]:
    statement = select(Project).order_by(Project.created_at.desc())

    return list(
        db.scalars(statement).all()
    )


def search_projects(
    db: Session,
    project_code: str | None = None,
    project_name: str | None = None,
    client_name: str | None = None,
    status: str | None = None,
    priority: str | None = None,
) -> list[Project]:

    conditions = []

    if project_code:
        conditions.append(
            Project.project_code.ilike(
                f"%{project_code}%"
            )
        )

    if project_name:
        conditions.append(
            Project.project_name.ilike(
                f"%{project_name}%"
            )
        )

    if client_name:
        conditions.append(
            Project.client_name.ilike(
                f"%{client_name}%"
            )
        )

    if status:
        conditions.append(
            Project.status == status
        )

    if priority:
        conditions.append(
            Project.priority == priority
        )

    statement = select(Project)

    if conditions:
        statement = statement.where(
            *conditions
        )

    statement = statement.order_by(
        Project.created_at.desc()
    )

    return list(
        db.scalars(statement).all()
    )


def get_project(
    db: Session,
    project_id: str,
) -> Project | None:
    return db.get(
        Project,
        project_id,
    )


def create_project(
    db: Session,
    project_data: ProjectCreate,
) -> Project:

    existing_project = db.scalar(
        select(Project).where(
            Project.project_code == project_data.project_code
        )
    )

    if existing_project is not None:
        raise ValueError(
            "Project code already exists"
        )

    project = Project(
        project_code=project_data.project_code,
        project_name=project_data.project_name,
        client_name=project_data.client_name,
        description=project_data.description,
        start_date=project_data.start_date,
        end_date=project_data.end_date,
        status=project_data.status,
        priority=project_data.priority,
    )

    db.add(project)

    try:
        db.commit()

    except IntegrityError:
        db.rollback()

        raise ValueError(
            "Project code already exists"
        )

    db.refresh(project)

    return project


def update_project(
    db: Session,
    project: Project,
    project_data: ProjectUpdate,
) -> Project:

    update_data = project_data.model_dump(
        exclude_unset=True
    )

    if "project_code" in update_data:

        existing_project = db.scalar(
            select(Project).where(
                Project.project_code
                == update_data["project_code"],
                Project.project_id
                != project.project_id,
            )
        )

        if existing_project is not None:
            raise ValueError(
                "Project code already exists"
            )

    for field, value in update_data.items():
        setattr(
            project,
            field,
            value,
        )

    try:
        db.commit()

    except IntegrityError:
        db.rollback()

        raise ValueError(
            "Project code already exists"
        )

    db.refresh(project)

    return project


def get_project_employees(
    db: Session,
    project_id: str,
) -> list[Employee]:

    statement = (
        select(Employee)
        .join(
            Allocation,
            Allocation.employee_id
            == Employee.employee_id,
        )
        .where(
            Allocation.project_id
            == project_id,
            Allocation.status == "active",
        )
        .order_by(
            Employee.created_at.desc()
        )
    )

    return list(
        db.scalars(statement).unique().all()
    )