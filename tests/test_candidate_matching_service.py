from types import SimpleNamespace

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.database.connection import Base
from app.models.entities import (
    Employee,
    EmployeeSkill,
    Skill,
)
from app.services.candidate_matching_service import (
    discover_candidate_employees,
)


def create_test_database():
    engine = create_engine(
        "sqlite:///:memory:",
        future=True,
    )

    Base.metadata.create_all(
        engine,
        tables=[
            Employee.__table__,
            Skill.__table__,
            EmployeeSkill.__table__,
        ],
    )

    return engine


def create_employee(
    employee_id: str,
    employee_code: str,
    name: str,
    email: str,
    status: str = "active",
) -> Employee:
    return Employee(
        employee_id=employee_id,
        employee_code=employee_code,
        name=name,
        email=email,
        status=status,
        experience_years=5,
        availability_status="available",
        utilization_percentage=0,
    )


def create_skill(
    skill_id: str,
    skill_name: str,
) -> Skill:
    return Skill(
        skill_id=skill_id,
        skill_name=skill_name,
    )


def create_employee_skill(
    employee_id: str,
    skill_id: str,
) -> EmployeeSkill:
    return EmployeeSkill(
        employee_id=employee_id,
        skill_id=skill_id,
        proficiency_level="advanced",
        years_experience=3,
    )


def create_requirement(
    required_skill_ids: list[str],
):
    return SimpleNamespace(
        required_skills=[
            SimpleNamespace(
                skill_id=skill_id,
            )
            for skill_id in required_skill_ids
        ]
    )


def test_discover_candidate_employees_requires_all_required_skills():
    engine = create_test_database()

    with Session(engine) as db:
        python_skill = create_skill(
            "skill-python",
            "Python",
        )
        sql_skill = create_skill(
            "skill-sql",
            "SQL",
        )

        employee_all_skills = create_employee(
            "employee-001",
            "EMP001",
            "Alice",
            "alice@example.com",
        )

        employee_missing_sql = create_employee(
            "employee-002",
            "EMP002",
            "Bob",
            "bob@example.com",
        )

        db.add_all(
            [
                python_skill,
                sql_skill,
                employee_all_skills,
                employee_missing_sql,
            ]
        )

        db.flush()

        db.add_all(
            [
                create_employee_skill(
                    "employee-001",
                    "skill-python",
                ),
                create_employee_skill(
                    "employee-001",
                    "skill-sql",
                ),
                create_employee_skill(
                    "employee-002",
                    "skill-python",
                ),
            ]
        )

        db.commit()

        requirement = create_requirement(
            [
                "skill-python",
                "skill-sql",
            ]
        )

        candidates = discover_candidate_employees(
            db,
            requirement,
        )

        candidate_ids = [
            employee.employee_id
            for employee in candidates
        ]

        assert candidate_ids == [
            "employee-001",
        ]


def test_discover_candidate_employees_excludes_inactive_employees():
    engine = create_test_database()

    with Session(engine) as db:
        python_skill = create_skill(
            "skill-python",
            "Python",
        )

        active_employee = create_employee(
            "employee-001",
            "EMP001",
            "Alice",
            "alice@example.com",
            status="active",
        )

        inactive_employee = create_employee(
            "employee-002",
            "EMP002",
            "Bob",
            "bob@example.com",
            status="inactive",
        )

        db.add_all(
            [
                python_skill,
                active_employee,
                inactive_employee,
            ]
        )

        db.flush()

        db.add_all(
            [
                create_employee_skill(
                    "employee-001",
                    "skill-python",
                ),
                create_employee_skill(
                    "employee-002",
                    "skill-python",
                ),
            ]
        )

        db.commit()

        requirement = create_requirement(
            [
                "skill-python",
            ]
        )

        candidates = discover_candidate_employees(
            db,
            requirement,
        )

        candidate_ids = [
            employee.employee_id
            for employee in candidates
        ]

        assert candidate_ids == [
            "employee-001",
        ]


def test_discover_candidate_employees_returns_all_active_employees_without_skill_requirement():
    engine = create_test_database()

    with Session(engine) as db:
        employee_a = create_employee(
            "employee-001",
            "EMP001",
            "Alice",
            "alice@example.com",
        )

        employee_b = create_employee(
            "employee-002",
            "EMP002",
            "Bob",
            "bob@example.com",
        )

        inactive_employee = create_employee(
            "employee-003",
            "EMP003",
            "Charlie",
            "charlie@example.com",
            status="inactive",
        )

        db.add_all(
            [
                employee_b,
                employee_a,
                inactive_employee,
            ]
        )

        db.commit()

        requirement = create_requirement([])

        candidates = discover_candidate_employees(
            db,
            requirement,
        )

        candidate_ids = [
            employee.employee_id
            for employee in candidates
        ]

        assert candidate_ids == [
            "employee-001",
            "employee-002",
        ]


def test_discover_candidate_employees_returns_deterministic_name_and_id_order():
    engine = create_test_database()

    with Session(engine) as db:
        employee_b = create_employee(
            "employee-002",
            "EMP002",
            "Same Name",
            "employee2@example.com",
        )

        employee_a = create_employee(
            "employee-001",
            "EMP001",
            "Same Name",
            "employee1@example.com",
        )

        employee_c = create_employee(
            "employee-003",
            "EMP003",
            "Another Name",
            "employee3@example.com",
        )

        db.add_all(
            [
                employee_b,
                employee_a,
                employee_c,
            ]
        )

        db.commit()

        requirement = create_requirement([])

        candidates = discover_candidate_employees(
            db,
            requirement,
        )

        candidate_ids = [
            employee.employee_id
            for employee in candidates
        ]

        assert candidate_ids == [
            "employee-003",
            "employee-001",
            "employee-002",
        ]


def test_discover_candidate_employees_returns_empty_when_no_employee_has_all_required_skills():
    engine = create_test_database()

    with Session(engine) as db:
        python_skill = create_skill(
            "skill-python",
            "Python",
        )
        sql_skill = create_skill(
            "skill-sql",
            "SQL",
        )

        employee_python_only = create_employee(
            "employee-001",
            "EMP001",
            "Alice",
            "alice@example.com",
        )

        employee_sql_only = create_employee(
            "employee-002",
            "EMP002",
            "Bob",
            "bob@example.com",
        )

        db.add_all(
            [
                python_skill,
                sql_skill,
                employee_python_only,
                employee_sql_only,
            ]
        )

        db.flush()

        db.add_all(
            [
                create_employee_skill(
                    "employee-001",
                    "skill-python",
                ),
                create_employee_skill(
                    "employee-002",
                    "skill-sql",
                ),
            ]
        )

        db.commit()

        requirement = create_requirement(
            [
                "skill-python",
                "skill-sql",
            ]
        )

        candidates = discover_candidate_employees(
            db,
            requirement,
        )

        assert candidates == []