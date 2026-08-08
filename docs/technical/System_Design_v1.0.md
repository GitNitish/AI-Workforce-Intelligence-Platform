# WorkforceIQ

# System Design Document (SDD)

---

## Document Information

| Item | Details |
|------|---------|
| Product Name | WorkforceIQ |
| Document Type | System Design Document (SDD) |
| Version | 1.0 |
| Status | Draft |
| Project Type | AI-Powered Workforce Management Platform |
| Methodology | Agile Scrum |
| Prepared By | Nitish Malik |
| Language | English |
| Repository | AI-Workforce-Intelligence-Platform |
| Parent Document | WorkforceIQ SRS Version 1.0 |
| Business Reference | WorkforceIQ BRD/PRD Version 1.0 |
| Development Phase | Gate 2 – Technical Design |

---

# 1. Introduction

## 1.1 Purpose

This System Design Document defines the technical architecture and design approach for WorkforceIQ Version 1.0.

The document translates the approved software requirements defined in the WorkforceIQ Software Requirements Specification (SRS) into a practical technical design that can be implemented, tested, deployed, and maintained.

The System Design Document defines:

- System architecture.
- Application layers.
- Major software components.
- Component responsibilities.
- Data flow.
- Service interactions.
- Security architecture.
- Authentication and authorization.
- AI recommendation architecture.
- Conversational Assistant architecture.
- Deployment architecture.
- Integration boundaries.
- Technical design decisions.
- Future extensibility considerations.

---

## 1.2 Relationship to Other Documents

The System Design Document is derived from the approved business and software requirements.

The relationship between the project artifacts is:

```text
Business Requirements
        │
        ▼
BRD / PRD
        │
        ▼
Software Requirements
        │
        ▼
SRS
        │
        ▼
System Design
        │
        ├───────────────┬─────────────────┐
        ▼               ▼                 ▼
Database Design   API Specification   UI/UX Design
        │               │                 │
        └───────────────┴─────────────────┘
                        │
                        ▼
                  Implementation
                        │
                        ▼
                      Testing
                        │
                        ▼
                    Deployment

The System Design Document shall remain traceable to the requirements defined in the SRS.

1.3 Design Objectives

The Version 1.0 system design shall achieve the following objectives:

Provide a clear separation between presentation, business logic, data access, and supporting services.
Support the functional requirements defined in the SRS.
Maintain strong validation and business-rule enforcement.
Protect workforce information through authentication and authorization.
Support deterministic AI-assisted resource recommendations.
Keep final allocation decisions under authorized human control.
Provide a controlled foundation for the Conversational Assistant.
Maintain data integrity across workforce and allocation operations.
Support auditability of material business actions.
Remain simple enough to implement and operate locally.
Avoid unnecessary architectural complexity.
Allow future extension without requiring complete redesign of the application.
1.4 Version 1.0 Design Philosophy

WorkforceIQ Version 1.0 shall use a modular monolithic architecture.

The system shall remain a single deployable application composed of logically separated modules rather than independent microservices.

The design prioritizes:

Simplicity.
Maintainability.
Testability.
Security.
Traceability.
Data integrity.
Clear business logic.
Controlled extensibility.

Microservices and distributed infrastructure are outside the mandatory Version 1.0 architecture.

2. System Architecture Overview
2.1 High-Level Architecture

The Version 1.0 architecture shall follow the structure below:

┌─────────────────────────────────────────────────────┐
│                    USER BROWSER                     │
│                                                     │
│                  React Frontend                     │
│                                                     │
│ Dashboard | Employees | Projects | Skills           │
│ Staffing | Allocation | Recommendations | Chat      │
└────────────────────────┬────────────────────────────┘
                         │
                    HTTP / REST
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│                  FASTAPI BACKEND                     │
│                                                     │
│ API / Routes                                        │
│        │                                            │
│        ▼                                            │
│ Request Validation / Schemas                        │
│        │                                            │
│        ▼                                            │
│ Business Services                                   │
│                                                     │
│ Employee │ Project │ Skills │ Allocation            │
│ Recommendation │ Dashboard │ Assistant              │
│                                                     │
│ Authentication │ Authorization │ Audit              │
│        │                                            │
│        ▼                                            │
│ Data Access Layer                                   │
└────────────────────────┬────────────────────────────┘
                         │
                    SQLAlchemy
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│                    SQLite                           │
│                                                     │
│ Employee                                            │
│ Project                                             │
│ Skill                                               │
│ Employee Skill                                      │
│ Certification                                      │
│ Staffing Requirement                                │
│ Allocation                                          │
│ User / Role / Permission                             │
│ Recommendation                                     │
│ Audit Event                                         │
└─────────────────────────────────────────────────────┘
2.2 Architecture Style

The application shall use a layered modular architecture.

The primary layers are:

Presentation Layer

Responsible for:

User interface.
User interaction.
Client-side validation.
Navigation.
Display of application responses.
Dashboard visualization.
Conversational interface.

Technology:

React

API Layer

Responsible for:

HTTP request handling.
Authentication context.
Request validation.
Response serialization.
API routing.
HTTP status handling.

Technology:

FastAPI

Business Service Layer

Responsible for:

Business rules.
Workforce operations.
Project operations.
Staffing logic.
Allocation logic.
Recommendation processing.
Dashboard calculations.
Conversational query processing.
Administrative operations.
Data Access Layer

Responsible for:

Database interaction.
Query execution.
Persistence.
Transaction handling.
Data retrieval.

Technology:

SQLAlchemy

Data Layer

Responsible for persistent Version 1.0 application data.

Technology:

SQLite

2.3 Component Interaction

The standard application interaction shall follow:

User
 │
 ▼
React Component
 │
 ▼
REST API
 │
 ▼
Validation
 │
 ▼
Business Service
 │
 ▼
Data Access
 │
 ▼
SQLite
 │
 ▼
Response
 │
 ▼
React UI

Business-critical operations shall not bypass the backend service layer.

2.4 Architecture Boundary

The Version 1.0 architecture shall contain the following major boundaries:

Frontend Boundary
        │
        ▼
API Boundary
        │
        ▼
Business Logic Boundary
        │
        ├───────────────┐
        ▼               ▼
AI / Assistant       Data Access
        │               │
        └───────┬───────┘
                ▼
             Database

The frontend shall not directly access the database.

AI and conversational functionality shall not bypass authentication, authorization, or approved business services.

3. Technology Stack
3.1 Frontend
Technology	Purpose
React	User interface
JavaScript / TypeScript as selected during implementation	Frontend development
Standard browser APIs	Client-side functionality

The final frontend language choice shall be maintained consistently throughout implementation.

3.2 Backend
Technology	Purpose
Python	Backend programming language
FastAPI	REST API framework
Pydantic / FastAPI validation	Request and response validation
JWT	Authentication tokens
Secure password hashing library	Password protection
3.3 Database
Technology	Purpose
SQLite	Version 1.0 relational database
SQLAlchemy	Database access and ORM abstraction

The database design shall be defined separately in the Database Design Document.

3.4 Testing

The implementation shall support appropriate automated and repeatable testing.

Testing technologies shall be finalized during the Test Strategy and implementation phases.

3.5 Version 1.0 Technology Constraint

The architecture shall not introduce unnecessary infrastructure such as:

Microservices.
Kubernetes.
Distributed service meshes.
Mandatory paid cloud services.
Enterprise integration platforms.
Production-scale distributed databases.

Such technologies may be considered in future releases if actual requirements justify them.

4. Major System Components
4.1 Employee Management Module

Responsible for:

Employee creation.
Employee retrieval.
Employee update.
Employee search.
Workforce profile management.
Availability information.
Utilization-related information.
Employee-skill relationships.
Certification relationships.

The module shall enforce the employee-related business rules defined in the SRS.

4.2 Project Management Module

Responsible for:

Project creation.
Project retrieval.
Project updates.
Project status.
Project search.
Staffing requirements.
Project workforce visibility.
4.3 Skills Management Module

Responsible for:

Standardized skills.
Employee skill assignments.
Proficiency levels.
Certifications.
Skill search.
Skill-related validation.
4.4 Staffing Requirement Module

Responsible for:

Staffing requirement creation.
Required quantity.
Required skills.
Required proficiency.
Required experience.
Required certifications.
Staffing dates.
Requirement status.
4.5 Resource Allocation Module

Responsible for:

Candidate selection.
Allocation validation.
Allocation creation.
Allocation conflict detection.
Capacity validation.
Availability validation.
Resource release.
Workforce-state updates.

The allocation module shall remain the authoritative component for final allocation creation.

4.6 Recommendation Module

Responsible for:

Candidate retrieval.
Mandatory eligibility filtering.
Recommendation scoring.
Candidate ranking.
Recommendation response generation.

The recommendation module shall not directly create final allocation records.

4.7 Dashboard Module

Responsible for:

Workforce utilization.
Bench visibility.
Allocation metrics.
Skill distribution.
Executive KPIs.
Workforce summary information.

Dashboard calculations shall use authoritative application data.

4.8 Conversational Assistant Module

Responsible for:

Supported natural-language workforce queries.
Query interpretation.
Authorization-aware information retrieval.
Response generation.
No-result handling.
Unsupported-query handling.

The Assistant shall operate within the approved Version 1.0 workforce-management scope.

4.9 Authentication Module

Responsible for:

User authentication.
Password verification.
Token generation.
Token validation.
Session-related authentication state.
4.10 Authorization Module

Responsible for:

Role validation.
Permission enforcement.
Protected-resource access.
Administrative access control.

Authorization shall be enforced server-side.

4.11 Audit Module

Responsible for recording material business and security events.

Examples include:

Authentication events.
Authorization failures.
Employee changes.
Allocation creation.
Resource release.
Administrative changes.
Other material business actions.
4.12 Logging Module

Responsible for:

Application events.
Operational errors.
Service failures.
Database failures.
Recommendation failures.
Security-related operational information.

Sensitive credentials shall not be logged.

5. Core Architecture Principle

The core WorkforceIQ business flow shall be:

Workforce Data
      │
      ▼
Project / Staffing Requirement
      │
      ▼
Candidate Identification
      │
      ▼
Eligibility Validation
      │
      ▼
Recommendation Scoring
      │
      ▼
Candidate Ranking
      │
      ▼
Human Review
      │
      ▼
Current-State Revalidation
      │
      ▼
Allocation
      │
      ▼
Workforce State Update
      │
      ▼
Audit
      │
      ▼
Dashboard Visibility

The system design shall preserve this sequence across the relevant modules.

6. Design Principles

The following principles shall guide the implementation of the WorkforceIQ architecture:

6.1 Single Source of Business Logic

Business-critical rules shall be centralized within backend services rather than duplicated across frontend components.

6.2 Backend as Security Boundary

The backend shall remain the authoritative security boundary for authentication, authorization, and protected operations.

6.3 Database as Persistence Boundary

Application components shall interact with persistent data through the approved data-access layer.

6.4 AI as Decision Support

The recommendation engine shall support human decision-making rather than independently making final workforce allocation decisions.

6.5 Modular Monolith

The application shall remain logically modular while operating as a single deployable Version 1.0 application.

6.6 Traceability

Major components shall remain traceable to SRS requirements and business objectives.

6.7 Testability

Business logic shall be structured so that important components can be tested independently.

6.8 Controlled Complexity

Technical complexity shall be introduced only when justified by an actual requirement.

7. Initial Architecture Baseline

The architecture defined in this section establishes the initial Version 1.0 technical baseline.

Detailed database structures, REST endpoint contracts, UI component specifications, test procedures, and deployment commands shall be defined in their respective project documents.

The implementation shall remain aligned with this architecture unless a material technical change is identified and evaluated through the project's change-management process.

# 8. Detailed Application Architecture

## 8.1 Backend Module Structure

The backend shall be organized into logical modules based on business responsibility.

A representative structure shall be:

```text
backend/
├── app/
│   ├── main.py
│   │
│   ├── api/
│   │   ├── auth.py
│   │   ├── employees.py
│   │   ├── projects.py
│   │   ├── skills.py
│   │   ├── staffing.py
│   │   ├── recommendations.py
│   │   ├── allocations.py
│   │   ├── dashboard.py
│   │   ├── assistant.py
│   │   └── admin.py
│   │
│   ├── schemas/
│   │
│   ├── services/
│   │   ├── employee_service.py
│   │   ├── project_service.py
│   │   ├── skill_service.py
│   │   ├── staffing_service.py
│   │   ├── recommendation_service.py
│   │   ├── allocation_service.py
│   │   ├── dashboard_service.py
│   │   ├── assistant_service.py
│   │   ├── auth_service.py
│   │   └── audit_service.py
│   │
│   ├── models/
│   │
│   ├── repositories/
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── logging.py
│   │
│   └── database/
│
└── tests/

8.2 API Layer

The API layer shall act as the entry point for frontend requests.

Responsibilities include:

Routing.
Authentication dependency handling.
Request validation.
Calling business services.
Returning structured responses.
HTTP error handling.

The API layer shall not contain extensive business logic.

8.3 Schema Layer

The schema layer shall define structured request and response contracts.

Schemas shall be used for:

Input validation.
Output serialization.
Data-type validation.
Required-field validation.
API consistency.
8.4 Service Layer

The service layer shall contain the primary business logic.

Examples:

EmployeeService
ProjectService
SkillService
StaffingService
RecommendationService
AllocationService
DashboardService
AssistantService
AuthService
AuditService

Services shall coordinate business rules and data-access operations.

8.5 Repository / Data Access Layer

The repository layer shall provide controlled interaction with SQLAlchemy and the database.

Responsibilities include:

Queries.
Inserts.
Updates.
Deletes where applicable.
Relationship retrieval.
Transaction support.

The repository layer shall not contain UI behavior.

9. Resource Allocation Architecture
9.1 Allocation Flow

The resource allocation workflow shall follow:

User
 │
 ▼
Select Project / Staffing Requirement
 │
 ▼
Request Candidates
 │
 ▼
Recommendation Service
 │
 ▼
Candidate Results
 │
 ▼
Human Review
 │
 ▼
Select Candidate
 │
 ▼
Allocation Service
 │
 ▼
Current-State Validation
 │
 ├── Invalid ──► Reject
 │
 ▼
Create Allocation
 │
 ▼
Update Workforce State
 │
 ▼
Create Audit Event
 │
 ▼
Return Allocation Result
9.2 Allocation Validation

The Allocation Service shall validate, where applicable:

Employee existence.
Project existence.
Staffing requirement existence.
User authorization.
Employee eligibility.
Skill requirements.
Proficiency requirements.
Certification requirements.
Experience requirements.
Availability.
Capacity.
Date validity.
Existing allocation conflicts.
9.3 Allocation Transaction Boundary

Allocation creation shall be treated as a business transaction.

The implementation shall avoid a situation where:

Allocation Created
       ↓
Workforce State Update Fails

leaves the application in an inconsistent state.

Where multiple related database changes are required, they shall be handled within an appropriate transaction boundary.

9.4 Current-State Revalidation

Candidate recommendations may become stale between recommendation generation and final allocation.

Therefore:

Recommendation
      ↓
Time Passes
      ↓
Workforce State Changes
      ↓
Allocation Request
      ↓
Current-State Validation
      ↓
Accept / Reject

The Allocation Service shall remain authoritative for the final validation.

10. AI Recommendation Architecture
10.1 Recommendation Flow

Version 1.0 shall use a deterministic recommendation architecture:

Staffing Requirement
        │
        ▼
Candidate Retrieval
        │
        ▼
Mandatory Eligibility Filter
        │
        ├── No Eligible Candidates
        │          │
        │          ▼
        │     No-Match Response
        │
        ▼
Eligible Candidates
        │
        ▼
Scoring
        │
        ▼
Ranking
        │
        ▼
Recommendation Response
        │
        ▼
Human Review
10.2 Mandatory Eligibility

Mandatory criteria shall be evaluated before preference-based scoring.

Examples include:

Required skill.
Required proficiency.
Required experience.
Required certification.
Required availability.

A candidate failing a mandatory criterion shall not receive a recommendation merely because of a high overall score.

10.3 Recommendation Scoring

The Version 1.0 scoring service shall use approved workforce factors such as:

Skill match.
Proficiency.
Experience.
Certification.
Availability.
Utilization.

The exact scoring weights shall be maintained as implementation configuration or documented business rules.

10.4 Deterministic Behavior

For identical:

Workforce data.
Staffing requirement.
Scoring configuration.

the recommendation engine shall produce consistent results.

10.5 Recommendation Response

A recommendation response should contain sufficient structured information for the user to understand the result.

Representative information includes:

Candidate
Eligibility
Score
Rank
Matched Skills
Proficiency
Experience
Certification Status
Availability
Utilization

The exact API response shall be defined in the API Specification.

10.6 Recommendation and Allocation Separation

The recommendation component shall not directly create allocation records.

The separation shall remain:

Recommendation Service
        │
        ▼
Recommendation
        │
        ▼
Human Decision
        │
        ▼
Allocation Service
        │
        ▼
Final Allocation

This preserves human decision authority.

11. Conversational Assistant Architecture
11.1 Assistant Flow

The Version 1.0 Conversational Assistant shall follow:

User Query
    │
    ▼
Authenticated User Context
    │
    ▼
Query Interpretation
    │
    ▼
Scope Validation
    │
    ├── Unsupported ──► Controlled Response
    │
    ▼
Authorization Check
    │
    ▼
Workforce Data Query
    │
    ▼
Result Validation
    │
    ▼
Natural-Language Response
11.2 Supported Query Scope

The Assistant shall support approved workforce-management queries including:

Employee search.
Skill-based search.
Project information.
Availability.
Utilization.
Supported workforce KPIs.
11.3 Query Authorization

The Assistant shall operate using the authenticated user's authorization context.

A user shall not gain access to restricted information by expressing the request through natural language.

The following principle shall apply:

Direct API Request
        │
        ├── Authorization
        │
        ▼
Allowed Data

Conversational Request
        │
        ├── Same Authorization
        │
        ▼
Allowed Data
11.4 Assistant Data Source

The Assistant shall use authoritative WorkforceIQ application data.

It shall not independently invent workforce facts.

11.5 No-Result Handling

If a supported query produces no matching data, the Assistant shall provide an appropriate no-result response.

It shall not fabricate a result.

11.6 Unsupported Query Handling

Queries outside the approved Version 1.0 scope shall return a controlled response.

The Assistant shall not automatically become a general-purpose chatbot.

12. Authentication and Authorization Architecture
12.1 Authentication Flow

The authentication flow shall be:

User
 │
 ▼
Login
 │
 ▼
Authentication API
 │
 ▼
Credential Verification
 │
 ├── Invalid ──► Authentication Failure
 │
 ▼
JWT Generation
 │
 ▼
Client
 │
 ▼
Authenticated API Requests
12.2 Protected Request Flow
API Request
     │
     ▼
Extract Token
     │
     ▼
Validate Token
     │
 ├── Invalid ──► 401
 │
 ▼
Identify User
     │
     ▼
Determine Role / Permissions
     │
 ├── Unauthorized ──► 403
 │
 ▼
Execute Business Operation
12.3 Role-Based Authorization

Authorization shall use the approved application roles:

Resource Manager.
Delivery Manager.
HR Executive.
Practice Manager.
Executive Leadership.
Employee.
System Administrator.

The exact permissions associated with each role shall be maintained in the API and authorization design.

12.4 Server-Side Authorization

Authorization shall be enforced by backend services or authorization dependencies.

Frontend visibility controls shall not be considered sufficient protection.

13. Dashboard Architecture
13.1 Dashboard Data Flow

Dashboard information shall follow:

Database
    │
    ▼
Data Access
    │
    ▼
Dashboard Service
    │
    ▼
Metric Calculation
    │
    ▼
Authorization
    │
    ▼
Dashboard API
    │
    ▼
React Dashboard
13.2 Dashboard Metrics

Version 1.0 dashboard functionality may include:

Workforce utilization.
Bench strength.
Allocation status.
Skill distribution.
Staffing status.
Executive KPIs.

Metrics shall use defined business calculations rather than independent frontend calculations.

13.3 Dashboard Authorization

Dashboard APIs shall verify whether the authenticated user is permitted to view the requested workforce information.

14. Data Flow Architecture
14.1 Employee Data Flow
User
 │
 ▼
Employee UI
 │
 ▼
Employee API
 │
 ▼
Employee Service
 │
 ▼
Employee Repository
 │
 ▼
SQLite
14.2 Project Data Flow
User
 │
 ▼
Project UI
 │
 ▼
Project API
 │
 ▼
Project Service
 │
 ▼
Project Repository
 │
 ▼
SQLite
14.3 Staffing Requirement Data Flow
Project
 │
 ▼
Staffing Requirement UI
 │
 ▼
Staffing API
 │
 ▼
Staffing Service
 │
 ▼
Validation
 │
 ▼
Database
14.4 Recommendation Data Flow
Staffing Requirement
       │
       ▼
Recommendation API
       │
       ▼
Recommendation Service
       │
       ├── Employee Data
       ├── Skills
       ├── Certifications
       ├── Availability
       └── Utilization
       │
       ▼
Eligibility
       │
       ▼
Scoring
       │
       ▼
Ranking
       │
       ▼
Recommendation Response
14.5 Allocation Data Flow
Selected Candidate
       │
       ▼
Allocation API
       │
       ▼
Allocation Service
       │
       ▼
Current-State Validation
       │
       ▼
Transaction
       │
       ├── Allocation
       ├── Workforce State
       └── Audit Event
       │
       ▼
Allocation Response
15. API and Service Interaction
15.1 General Interaction Pattern

The standard backend interaction shall be:

HTTP Request
     │
     ▼
API Route
     │
     ▼
Request Schema
     │
     ▼
Authentication
     │
     ▼
Authorization
     │
     ▼
Business Service
     │
     ▼
Repository
     │
     ▼
Database
     │
     ▼
Service Result
     │
     ▼
Response Schema
     │
     ▼
HTTP Response
15.2 Business Service Independence

Business services should remain independently testable where practical.

For example:

AllocationService
      │
      ├── Validation
      ├── Capacity
      ├── Conflict Detection
      └── Persistence

The service should not depend directly on React or browser behavior.

15.3 Service Reuse

Where multiple application features require the same business calculation, the calculation should be implemented in a shared service rather than duplicated.

Examples include:

Availability calculation.
Utilization calculation.
Eligibility validation.
Permission validation.
16. Error Handling Architecture
16.1 Error Flow

Errors shall follow:

Operation
   │
   ▼
Validation / Processing
   │
   ├── Validation Error
   ├── Authentication Error
   ├── Authorization Error
   ├── Not Found
   ├── Conflict
   ├── Business Rule Error
   └── Unexpected Error
            │
            ▼
       Error Handler
            │
            ├── Log
            │
            ▼
       Safe API Response
            │
            ▼
        Frontend
16.2 Error Categories

The implementation shall distinguish between:

Input validation errors.
Authentication failures.
Authorization failures.
Missing resources.
Business-rule violations.
Data conflicts.
System errors.
16.3 Sensitive Error Protection

Unexpected errors shall not expose:

Stack traces.
Password information.
Authentication secrets.
Database credentials.
Internal infrastructure details.

Detailed diagnostic information shall remain in controlled logs.

17. Audit Architecture
17.1 Audit Flow

Material business events shall follow:

Business Operation
       │
       ▼
Operation Result
       │
       ▼
Audit Service
       │
       ▼
Audit Event
       │
       ▼
Database
17.2 Auditable Operations

The system should record relevant events including:

Authentication.
Authorization failures.
Employee changes.
Project changes.
Staffing requirement changes.
Allocation creation.
Resource release.
Administrative changes.
Material recommendation events where required.
17.3 Audit Data

Audit records should contain:

User.
Action.
Entity.
Entity identifier.
Timestamp.
Result.
Relevant metadata.
18. Logging Architecture
18.1 Logging Flow
Application Component
        │
        ▼
Logging Service / Framework
        │
        ▼
Application Logs

Logging shall support operational troubleshooting without exposing sensitive information.

18.2 Logging Levels

The implementation may support:

DEBUG
INFO
WARNING
ERROR
CRITICAL

Development environments may use more verbose logging than production-oriented environments.

18.3 Correlation

Where practical, API requests and significant operations should include a correlation or request identifier to support troubleshooting across application logs.

19. Security Architecture
19.1 Security Boundaries

Security shall be enforced across multiple layers:

Browser
   │
   ▼
Authentication
   │
   ▼
Authorization
   │
   ▼
API Validation
   │
   ▼
Business Rules
   │
   ▼
Database Integrity

No individual layer shall be assumed to provide all security protection.

19.2 Input Security

The application shall validate:

Required fields.
Data types.
Allowed values.
Field lengths.
Business constraints.

Invalid input shall be rejected before unsafe processing occurs.

19.3 Database Security

The application shall:

Use controlled database access.
Avoid exposing database files through the frontend.
Protect database credentials where applicable.
Use transactions for business-critical multi-step operations.
19.4 Secret Protection

Secrets shall remain outside source code wherever practical.

Examples include:

JWT secret.
API keys.
Database credentials.
External-service credentials.
19.5 AI Security

AI-assisted functionality shall respect:

Authentication.
Authorization.
Data access controls.
Business rules.
Human decision authority.

AI functionality shall not create a bypass around application security.

20. Deployment Architecture
20.1 Version 1.0 Deployment

The Version 1.0 deployment shall support local execution.

The logical deployment structure shall be:

Local Machine
│
├── React Frontend
│
├── FastAPI Backend
│
├── SQLite Database
│
└── Configuration / Environment
20.2 Runtime Interaction
Browser
   │
   ▼
React Development / Application Server
   │
   ▼
FastAPI
   │
   ▼
SQLite

The exact development ports and startup commands shall be documented in the Deployment Guide.

20.3 Deployment Simplicity

Version 1.0 shall not require paid cloud infrastructure to demonstrate core functionality.

Future cloud deployment may be introduced if business or operational requirements justify it.

21. Scalability and Extensibility
21.1 Modular Growth

The modular structure shall allow future growth in:

Employees.
Projects.
Skills.
Allocations.
Users.
Workforce queries.

without requiring complete application redesign.

21.2 Database Migration Path

SQLAlchemy shall provide an abstraction between business services and the underlying relational database.

This design should make a future migration from SQLite to a production-oriented relational database such as PostgreSQL more manageable.

A migration shall still require:

Schema validation.
Data migration.
Performance testing.
Configuration changes.
Deployment changes.
21.3 Future AI Evolution

The recommendation architecture shall allow future enhancement toward:

Machine-learning-based recommendations.
Predictive workforce analytics.
Historical allocation analysis.
Skill-gap analysis.
Workforce forecasting.

Such capabilities are outside the mandatory Version 1.0 implementation.

21.4 Future Integration

The modular API boundary shall allow future integrations with:

Enterprise HR systems.
Project management systems.
Identity providers.
Notification systems.
Enterprise analytics platforms.

Such integrations shall require separate requirements and design assessments.

22. Key Architecture Decisions
22.1 Modular Monolith Instead of Microservices
Decision

Use a modular monolithic architecture for Version 1.0.

Reason

The system is being developed as a focused Version 1.0 application with a controlled scope and local deployment requirement.

Microservices would introduce additional:

Deployment complexity.
Network boundaries.
Monitoring requirements.
Infrastructure overhead.
Failure modes.

without providing sufficient Version 1.0 benefit.

22.2 SQLite for Version 1.0
Decision

Use SQLite as the Version 1.0 database.

Reason

SQLite provides:

Zero infrastructure setup.
Local persistence.
Simple development.
Easy demonstration.
Low operational overhead.

The architecture retains SQLAlchemy as the database abstraction layer to support future migration.

22.3 FastAPI for Backend
Decision

Use FastAPI.

Reason

FastAPI provides:

Python-based development.
REST API support.
Request validation.
API documentation.
Strong integration with Pydantic.
Suitable performance for the Version 1.0 workload.
22.4 React for Frontend
Decision

Use React.

Reason

React provides:

Component-based UI development.
Reusable interface components.
Suitable dashboard implementation.
Clear separation between frontend and backend APIs.
22.5 Deterministic Recommendation Engine
Decision

Use deterministic eligibility filtering and scoring for Version 1.0.

Reason

This approach provides:

Predictable behavior.
Explainable recommendations.
Easier testing.
Easier debugging.
Controlled business rules.
No training dataset dependency.

Machine-learning recommendation is deferred to a future release.

22.6 Human-Controlled Allocation
Decision

Keep final allocation authority with an authorized user.

Reason

Resource allocation affects real workforce decisions.

The recommendation engine should assist the decision-maker rather than independently commit an allocation.

23. Architecture Traceability
23.1 Requirement-to-Component Mapping
Requirement Area	Primary Component
Employee Management	Employee Service
Project Management	Project Service
Skills	Skill Service
Staffing Requirements	Staffing Service
Candidate Search	Recommendation / Workforce Services
AI Recommendations	Recommendation Service
Resource Allocation	Allocation Service
Resource Release	Allocation Service
Dashboards	Dashboard Service
Conversational Assistant	Assistant Service
Authentication	Authentication Module
Authorization	Authorization Module
Administration	Administration Module
Audit	Audit Service
Logging	Logging Framework / Service
23.2 Design-to-Requirement Traceability

The detailed technical artifacts shall maintain the following relationship:

SRS Requirement
      │
      ▼
System Component
      │
      ▼
Database Entity / API
      │
      ▼
Frontend Workflow
      │
      ▼
Test Case

The Database Design, API Specification, UI/UX Specification, and Test Strategy shall extend this traceability.

24. System Design Completion Criteria

The System Design Document shall be considered complete when:

The Version 1.0 architecture is defined.
Major system components are defined.
Component responsibilities are documented.
Technology choices are documented.
Backend architecture is defined.
Frontend architecture is defined.
Database interaction is defined.
Authentication and authorization architecture is defined.
Allocation architecture is defined.
AI recommendation architecture is defined.
Conversational Assistant architecture is defined.
Dashboard architecture is defined.
Error handling is defined.
Audit and logging are defined.
Security architecture is defined.
Deployment architecture is defined.
Future extensibility is defined.
Major architecture decisions are documented.
Requirement traceability is established.
The design is ready to support detailed database, API, UI/UX, testing, and implementation work.
25. System Design Baseline

The System Design Document establishes the Version 1.0 technical architecture baseline for WorkforceIQ.

The architecture intentionally uses a modular monolith with React, FastAPI, SQLAlchemy, and SQLite to provide a practical, testable, locally deployable system.

The design separates:

Presentation.
API handling.
Business services.
Recommendation logic.
Conversational Assistant logic.
Authentication.
Authorization.
Data access.
Persistence.
Audit.
Logging.

The architecture shall remain aligned with the approved SRS.

Material architectural changes identified during implementation shall be assessed through the project's change-management process rather than introduced informally.

26. End of System Design Document

This document defines the Version 1.0 technical design baseline for WorkforceIQ.

Detailed implementation contracts shall be defined in the Database Design Document, API Specification, UI/UX Specification, Test Strategy, and Deployment Guide.

The next technical design activity shall be the creation of the Version 1.0 Database Design Document.


