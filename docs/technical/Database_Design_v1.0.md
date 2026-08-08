# WorkforceIQ

# Database Design Document (DBD)

---

## Document Information

| Item | Details |
|------|---------|
| Product Name | WorkforceIQ |
| Document Type | Database Design Document (DBD) |
| Version | 1.0 |
| Status | Draft |
| Project Type | AI-Powered Workforce Management Platform |
| Methodology | Agile Scrum |
| Prepared By | Nitish Malik |
| Language | English |
| Repository | AI-Workforce-Intelligence-Platform |
| Parent Document | WorkforceIQ System Design Document Version 1.0 |
| Requirements Reference | WorkforceIQ SRS Version 1.0 |
| Business Reference | WorkforceIQ BRD/PRD Version 1.0 |
| Database | SQLite |
| ORM / Data Access | SQLAlchemy |
| Development Phase | Gate 2 – Technical Design |

---

# 1. Introduction

## 1.1 Purpose

This Database Design Document defines the logical and physical database design for WorkforceIQ Version 1.0.

The document translates the data requirements defined in the SRS and the architecture defined in the System Design Document into a structured relational database design.

The document defines:

- Database technology.
- Data entities.
- Entity relationships.
- Attributes.
- Primary keys.
- Foreign keys.
- Constraints.
- Relationships.
- Reference data.
- Audit data.
- Indexing considerations.
- Data integrity rules.
- Transaction considerations.
- Database access principles.
- Future database migration considerations.

---

## 1.2 Database Objectives

The Version 1.0 database shall:

1. Persist WorkforceIQ business data reliably.
2. Maintain referential integrity.
3. Support employee and workforce management.
4. Support project and staffing management.
5. Support skills and certification management.
6. Support resource allocation.
7. Support AI recommendation results where required.
8. Support authentication and authorization data.
9. Support audit records.
10. Support dashboard and workforce analytics queries.
11. Provide a clear relational structure.
12. Remain simple enough for local Version 1.0 deployment.
13. Support future migration to a production-oriented relational database if required.

---

## 1.3 Database Technology

Version 1.0 shall use:

| Technology | Purpose |
|------------|---------|
| SQLite | Relational database |
| SQLAlchemy | ORM and database access abstraction |

SQLite is selected for Version 1.0 because it provides:

- Local persistence.
- Minimal infrastructure requirements.
- Simple development setup.
- Easy demonstration.
- Low operational overhead.

The database design shall avoid unnecessary dependencies on SQLite-specific behavior where practical.

---

## 1.4 Database Architecture

The logical data-access architecture shall be:

```text
React Frontend
       │
       ▼
FastAPI API
       │
       ▼
Business Service Layer
       │
       ▼
Repository / Data Access Layer
       │
       ▼
SQLAlchemy
       │
       ▼
SQLite

2. Database Design Principles
2.1 Relational Design

WorkforceIQ Version 1.0 shall use a relational data model.

Entities shall be represented as relational tables with defined:

Primary keys.
Foreign keys.
Attributes.
Constraints.
Relationships.
2.2 Data Integrity

The database shall maintain data integrity through:

Primary keys.
Foreign keys.
NOT NULL constraints where required.
UNIQUE constraints where required.
CHECK constraints where appropriate.
Application-level business validation.
Transaction boundaries.
2.3 Referential Integrity

Relationships between entities shall be enforced through foreign-key relationships where appropriate.

Examples include:

Employee
   │
   ├── Employee Skill
   │
   ├── Certification
   │
   └── Allocation

and:

Project
   │
   ├── Staffing Requirement
   │
   └── Allocation
2.4 Business Rules vs Database Constraints

Not every business rule shall be implemented solely through database constraints.

Database constraints shall protect fundamental data integrity.

Complex business rules shall be enforced through backend services.

For example:

Database
   │
   └── Protects structural integrity

Backend Services
   │
   └── Protect business rules

API
   │
   └── Validates requests

Frontend
   │
   └── Provides user-friendly validation

The backend shall remain authoritative for business-rule enforcement.

2.5 Primary Key Strategy

Version 1.0 entities shall use stable unique identifiers.

The implementation shall use a consistent identifier strategy across entities.

Primary keys shall:

Uniquely identify records.
Remain stable after creation.
Be used by related records through foreign keys.
Avoid dependence on business-readable names.
3. Core Data Model
3.1 Core Entities

The Version 1.0 logical database model shall include the following major entities:

Employee
Skill
EmployeeSkill
Certification
Project
StaffingRequirement
Allocation
User
Role
Permission
RolePermission
Recommendation
AuditEvent

These entities support the major WorkforceIQ capabilities defined in the SRS.

3.2 Employee Entity

The Employee entity represents an individual workforce resource managed by WorkforceIQ.

Representative attributes include:

Attribute	Purpose
employee_id	Unique employee identifier
employee_code	Business-readable employee identifier
name	Employee name
email	Employee email
designation	Current designation
department	Organizational department
experience_years	Total relevant experience
availability_status	Current availability state
utilization_percentage	Current utilization
location	Workforce location
status	Employee record status
created_at	Record creation timestamp
updated_at	Last update timestamp

The final physical column definitions shall be established during implementation.

3.3 Skill Entity

The Skill entity represents a standardized workforce skill.

Representative attributes include:

Attribute	Purpose
skill_id	Unique skill identifier
skill_name	Standardized skill name
category	Skill category
description	Skill description
status	Active/inactive state
created_at	Record creation timestamp
updated_at	Last update timestamp

Skill names should be normalized to reduce duplicate skill records.

3.4 EmployeeSkill Entity

EmployeeSkill represents the many-to-many relationship between employees and skills.

Representative attributes include:

Attribute	Purpose
employee_skill_id	Unique relationship identifier
employee_id	Related employee
skill_id	Related skill
proficiency_level	Employee proficiency
years_experience	Experience with the skill
last_assessed_at	Last assessment date
created_at	Relationship creation timestamp
updated_at	Relationship update timestamp

The combination of employee and skill should not create unintended duplicate active relationships.

3.5 Certification Entity

The Certification entity represents employee certification information.

Representative attributes include:

Attribute	Purpose
certification_id	Unique certification identifier
employee_id	Related employee
certification_name	Certification name
issuing_authority	Issuing organization
certification_number	Certification reference where applicable
issue_date	Certification issue date
expiry_date	Certification expiry date
status	Current certification status
created_at	Record creation timestamp
updated_at	Last update timestamp
3.6 Project Entity

The Project entity represents a project requiring workforce resources.

Representative attributes include:

Attribute	Purpose
project_id	Unique project identifier
project_code	Business-readable project identifier
project_name	Project name
client_name	Client/customer
description	Project description
start_date	Project start date
end_date	Project end date
status	Project status
priority	Project priority
created_at	Record creation timestamp
updated_at	Last update timestamp
3.7 StaffingRequirement Entity

The StaffingRequirement entity represents a workforce requirement associated with a project.

Representative attributes include:

Attribute	Purpose
staffing_requirement_id	Unique requirement identifier
project_id	Related project
role_name	Required role
required_quantity	Number of resources required
required_experience	Minimum experience
required_proficiency	Minimum skill proficiency
start_date	Required staffing start
end_date	Required staffing end
priority	Staffing priority
status	Requirement status
created_at	Record creation timestamp
updated_at	Last update timestamp

Required skills and certifications shall be represented through appropriate relationship structures rather than storing multiple values in a single field.

3.8 Allocation Entity

The Allocation entity represents an approved assignment of an employee to a project or staffing requirement.

Representative attributes include:

Attribute	Purpose
allocation_id	Unique allocation identifier
employee_id	Allocated employee
project_id	Target project
staffing_requirement_id	Related staffing requirement
allocation_percentage	Allocation percentage
start_date	Allocation start
end_date	Allocation end
status	Allocation status
allocated_by	User who created the allocation
created_at	Allocation creation timestamp
updated_at	Last update timestamp

Allocation records shall represent final human-approved workforce decisions.

3.9 User Entity

The User entity represents an authenticated WorkforceIQ application user.

Representative attributes include:

Attribute	Purpose
user_id	Unique user identifier
username	Login identifier
email	User email
password_hash	Secure password representation
employee_id	Optional related employee
status	Account status
last_login_at	Last successful login
created_at	Account creation timestamp
updated_at	Account update timestamp

Plain-text passwords shall never be stored.

3.10 Role Entity

The Role entity represents an application authorization role.

Representative roles include:

Resource Manager.
Delivery Manager.
HR Executive.
Practice Manager.
Executive Leadership.
Employee.
System Administrator.

Representative attributes include:

Attribute	Purpose
role_id	Unique role identifier
role_name	Role name
description	Role description
status	Role status
created_at	Creation timestamp
updated_at	Update timestamp
3.11 Permission Entity

The Permission entity represents an individual application capability.

Examples include:

employee.read
employee.create
employee.update
project.read
project.create
project.update
allocation.read
allocation.create
allocation.release
recommendation.read
dashboard.read
user.manage
audit.read

The final permission catalogue shall be defined during API and authorization implementation.

3.12 RolePermission Entity

RolePermission represents the many-to-many relationship between roles and permissions.

Representative attributes include:

Attribute	Purpose
role_permission_id	Unique relationship identifier
role_id	Related role
permission_id	Related permission
created_at	Relationship creation timestamp

A role shall not contain duplicate permission assignments.

3.13 Recommendation Entity

The Recommendation entity represents a generated recommendation result where persistence is required.

Representative attributes include:

Attribute	Purpose
recommendation_id	Unique recommendation identifier
staffing_requirement_id	Related staffing requirement
employee_id	Recommended employee
score	Recommendation score
rank	Recommendation rank
eligibility_status	Eligibility result
recommendation_reason	Explainability information
generated_at	Recommendation timestamp
generated_by	User/request context where applicable

Recommendation records shall not be interpreted as final allocations.

3.14 AuditEvent Entity

The AuditEvent entity records material business and security events.

Representative attributes include:

Attribute	Purpose
audit_event_id	Unique audit identifier
user_id	User responsible for event
action	Action performed
entity_type	Affected entity
entity_id	Affected entity identifier
result	Operation result
event_timestamp	Event timestamp
metadata	Relevant non-sensitive context

Sensitive credentials shall not be stored in audit metadata.

4. Entity Relationships
4.1 Employee Relationships
Employee
   │
   ├──────────< EmployeeSkill >────────── Skill
   │
   ├──────────< Certification
   │
   ├──────────< Allocation
   │
   └──────────< Recommendation

An employee may have:

Multiple skills.
Multiple certifications.
Multiple allocations over time.
Multiple recommendation records.
4.2 Project Relationships
Project
   │
   ├──────────< StaffingRequirement
   │
   └──────────< Allocation

A project may contain multiple staffing requirements and multiple allocations.

4.3 Staffing Requirement Relationships
StaffingRequirement
        │
        ├────────── Project
        │
        ├──────────< Allocation
        │
        └──────────< Recommendation
4.4 Authorization Relationships
User
 │
 └────────── Role
                │
                └──────────< RolePermission >────────── Permission

The implementation may support one or multiple roles per user depending on the finalized authorization design.

4.5 Audit Relationships
User
 │
 └──────────< AuditEvent

Audit records may reference affected entities using entity type and entity identifier.

5. Cardinality Summary
Relationship	Cardinality
Employee → EmployeeSkill	1 : Many
Skill → EmployeeSkill	1 : Many
Employee → Certification	1 : Many
Project → StaffingRequirement	1 : Many
Project → Allocation	1 : Many
Employee → Allocation	1 : Many
StaffingRequirement → Allocation	1 : Many
StaffingRequirement → Recommendation	1 : Many
Employee → Recommendation	1 : Many
User → AuditEvent	1 : Many
Role → Permission	Many : Many

Many-to-many relationships shall be represented through explicit relationship tables.

6. Database Relationship Overview

The logical relationship model shall follow:

                         ┌─────────────┐
                         │    Skill    │
                         └──────┬──────┘
                                │
                                │
                         ┌──────▼──────┐
                         │EmployeeSkill│
                         └──────┬──────┘
                                │
                                │
┌─────────────┐          ┌──────▼──────┐
│Certification│          │   Employee  │
└──────┬──────┘          └──────┬──────┘
       │                        │
       │                        │
       │                 ┌──────▼──────┐
       │                 │  Allocation │
       │                 └──────┬──────┘
       │                        │
       │                 ┌──────▼──────┐
       │                 │   Project   │
       │                 └──────┬──────┘
       │                        │
       │                 ┌──────▼──────────┐
       └────────────────►│StaffingRequirement│
                         └────────┬─────────┘
                                  │
                         ┌────────▼────────┐
                         │ Recommendation  │
                         └─────────────────┘

Authorization and audit entities operate alongside the workforce data model:

User
 │
 ├──── Role ──── RolePermission ──── Permission
 │
 └──── AuditEvent
7. Database Integrity Baseline

The database design shall maintain:

Unique primary keys.
Valid foreign-key references.
Required-field constraints.
Appropriate uniqueness constraints.
Valid date relationships.
Valid allocation percentages.
Valid status values.
Valid proficiency values.
Valid relationship records.

Application-level validation shall complement database constraints.

8. Transaction Requirements

Business operations requiring multiple related database changes shall use transaction boundaries.

Important transaction candidates include:

Allocation creation.
Resource release.
Employee updates affecting related workforce state.
Role/permission updates.
Administrative operations affecting multiple records.

The application shall roll back a transaction when a critical operation fails before completion.

9. Database Access Principles

All database access shall occur through the backend application.

The application shall use SQLAlchemy for database interaction.

Direct SQL may be used only where technically justified and safely parameterized.

The application shall not construct unsafe SQL using untrusted user input.

10. Database Design Baseline

The logical database design defined in this document establishes the Version 1.0 data model baseline for WorkforceIQ.

The physical implementation may refine:

Column types.
Indexes.
Constraints.
Naming conventions.
Migration structure.

provided that the resulting implementation remains consistent with the approved requirements and system architecture.

Detailed API representations of database entities shall be defined in the API Specification.

The final physical schema shall be validated during implementation and testing.

11. Database Design Completion Criteria

The Database Design Document shall be considered complete when:

Core entities are defined.
Entity relationships are defined.
Primary-key strategy is defined.
Foreign-key relationships are defined.
Core attributes are identified.
Authorization entities are defined.
Recommendation persistence is defined.
Audit persistence is defined.
Data-integrity principles are defined.
Transaction requirements are defined.
Database access principles are defined.
The logical model is ready for implementation.
The database design is traceable to the SRS and System Design.
12. End of Database Design Document

This document defines the Version 1.0 logical database design for WorkforceIQ.

The next technical artifact shall define the REST API contracts that expose the approved workforce-management capabilities to the frontend and other authorized application components.

