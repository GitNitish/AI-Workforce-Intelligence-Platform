# WorkforceIQ

# API Specification

---

## Document Information

| Item | Details |
|------|---------|
| Product Name | WorkforceIQ |
| Document Type | API Specification |
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
| Backend Framework | FastAPI |
| API Style | REST |
| API Documentation | OpenAPI |
| Development Phase | Gate 2 – Technical Design |

---

# 1. Introduction

## 1.1 Purpose

This API Specification defines the REST API contract for WorkforceIQ Version 1.0.

The API provides the controlled interface between the React frontend and the FastAPI backend and exposes the workforce-management capabilities defined in the approved SRS.

The API shall provide controlled access to:

- Authentication.
- Employee management.
- Project management.
- Skills management.
- Staffing requirements.
- Candidate search.
- AI-assisted recommendations.
- Resource allocation.
- Resource release.
- Workforce dashboards.
- Conversational Assistant.
- Administration.
- Audit-related functionality.

---

## 1.2 API Design Objectives

The Version 1.0 API shall:

1. Provide predictable REST-based interfaces.
2. Validate incoming requests.
3. Return structured responses.
4. Enforce authentication for protected operations.
5. Enforce authorization server-side.
6. Apply business rules through backend services.
7. Return meaningful HTTP status codes.
8. Prevent unauthorized access to workforce information.
9. Maintain consistent error handling.
10. Support frontend integration through documented contracts.
11. Remain simple enough for Version 1.0 local deployment.
12. Support future API evolution without unnecessary breaking changes.

---

# 2. API Architecture

## 2.1 Request Flow

The standard API request flow shall be:

```text
React Frontend
      │
      ▼
HTTP Request
      │
      ▼
FastAPI Route
      │
      ▼
Request Validation
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
Repository / Data Access
      │
      ▼
Database
      │
      ▼
Service Response
      │
      ▼
Response Schema
      │
      ▼
HTTP Response
      │
      ▼
React Frontend

2.2 API Responsibility Boundary

The API layer shall be responsible for:

Routing.
Request parsing.
Request validation.
Authentication handling.
Authorization enforcement.
Calling business services.
Response serialization.
HTTP status handling.
Error response formatting.

The API layer shall not contain extensive business logic.

Business rules shall remain within backend service components.

2.3 API and Database Separation

The API shall not provide direct database access to clients.

The logical boundary shall remain:

Client
  │
  ▼
API
  │
  ▼
Business Service
  │
  ▼
Data Access Layer
  │
  ▼
Database
3. API Conventions
3.1 Base URL

The Version 1.0 API shall use a versioned API prefix.

Example:

/api/v1

The local development base URL may be:

http://localhost:<backend-port>/api/v1

The exact backend port shall be defined in the Deployment Guide.

3.2 HTTP Methods

The API shall use standard HTTP methods according to operation semantics.

Method	Primary Use
GET	Retrieve data
POST	Create resources or initiate supported operations
PUT	Replace or update resources where appropriate
PATCH	Partial update where appropriate
DELETE	Delete resources where explicitly supported

Business-critical operations shall use the method that best represents the intended behavior.

3.3 Resource Naming

API resource paths shall use consistent plural nouns.

Examples:

/api/v1/employees
/api/v1/projects
/api/v1/skills
/api/v1/staffing-requirements
/api/v1/allocations
/api/v1/recommendations

Resource names shall remain consistent across the API.

3.4 JSON Format

Version 1.0 API requests and responses shall use JSON unless a specific operation requires another representation.

Example:

{
  "employee_id": 101,
  "name": "Example Employee",
  "status": "available"
}
3.5 Content Type

JSON requests shall use:

Content-Type: application/json

Responses containing JSON shall use:

Content-Type: application/json
3.6 Date and Time Format

Dates shall use an unambiguous format.

Date example:

2026-08-08

Timestamp example:

2026-08-08T18:30:00Z

The implementation shall use a consistent timezone strategy for timestamps.

4. Authentication
4.1 Authentication Method

Version 1.0 shall use JWT-based authentication.

The authentication flow shall be:

User
 │
 ▼
Login API
 │
 ▼
Credential Validation
 │
 ├── Invalid ──► 401
 │
 ▼
JWT Token
 │
 ▼
Client
 │
 ▼
Authenticated Requests
4.2 Login Endpoint
Endpoint
POST /api/v1/auth/login
Purpose

Authenticates a WorkforceIQ user and returns an authentication token.

Request
{
  "username": "user@example.com",
  "password": "example-password"
}
Successful Response
200 OK
{
  "access_token": "<jwt-token>",
  "token_type": "bearer"
}
Authentication Failure
401 Unauthorized

The response shall not reveal whether the username or password was specifically incorrect.

4.3 Current User Endpoint
Endpoint
GET /api/v1/auth/me
Purpose

Returns information about the currently authenticated user.

Authentication

Required.

Successful Response
200 OK

Representative response:

{
  "user_id": 1,
  "username": "user@example.com",
  "roles": [
    "Resource Manager"
  ],
  "status": "active"
}
4.4 Authentication Header

Protected API requests shall use:

Authorization: Bearer <jwt-token>
5. Authorization
5.1 Authorization Principle

Authentication confirms the identity of the user.

Authorization determines whether the authenticated user is permitted to perform the requested operation.

Both controls shall be enforced server-side.

5.2 Authorization Flow
Request
  │
  ▼
JWT Validation
  │
  ▼
User Identification
  │
  ▼
Role / Permission Check
  │
  ├── Not Authorized ──► 403
  │
  ▼
Business Operation
5.3 Application Roles

Version 1.0 shall support the roles defined by the SRS:

Resource Manager.
Delivery Manager.
HR Executive.
Practice Manager.
Executive Leadership.
Employee.
System Administrator.

The exact role-to-permission mapping shall be implemented consistently with the approved authorization model.

5.4 Authorization Requirements

Protected endpoints shall:

Validate authentication.
Validate required permissions.
Reject unauthorized access.
Avoid relying solely on frontend controls.
Return appropriate HTTP status codes.
6. Common Response Structure
6.1 Successful Responses

Successful responses shall return structured JSON appropriate to the endpoint.

Single-resource example:

{
  "employee_id": 101,
  "name": "Example Employee",
  "status": "available"
}

Collection example:

{
  "items": [
    {
      "employee_id": 101,
      "name": "Example Employee"
    }
  ],
  "total": 1
}
6.2 Error Response Structure

Version 1.0 API errors shall use a consistent structure.

Example:

{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request contains invalid data.",
    "details": [
      {
        "field": "start_date",
        "message": "Start date is required."
      }
    ]
  }
}

The API shall avoid exposing internal stack traces or sensitive implementation details.

7. HTTP Status Codes

The API shall use standard HTTP status codes.

Status	Meaning
200	Successful request
201	Resource created
204	Successful request with no response body
400	Invalid request
401	Authentication required or failed
403	Authenticated but not authorized
404	Resource not found
409	Business/data conflict
422	Validation failure
429	Rate limit exceeded where applicable
500	Unexpected server error

The exact status code used shall depend on the operation and error condition.

8. Validation Principles
8.1 Request Validation

API requests shall validate:

Required fields.
Data types.
Allowed values.
String lengths.
Numeric ranges.
Date formats.
Date relationships.
Identifier formats.
8.2 Business Validation

Business validation shall occur in the backend service layer.

Examples include:

Employee availability.
Skill requirements.
Proficiency requirements.
Certification requirements.
Experience requirements.
Allocation capacity.
Allocation conflicts.
Project status.
Staffing requirement status.
8.3 Validation Boundary

The validation flow shall be:

Frontend Validation
       │
       ▼
API Schema Validation
       │
       ▼
Business Validation
       │
       ▼
Database Constraints

Frontend validation improves user experience but shall not be treated as the security or business-rule boundary.

9. API Documentation

FastAPI shall provide OpenAPI-compatible API documentation.

The generated API documentation shall reflect the implemented endpoint contracts.

Documentation should include:

Endpoint path.
HTTP method.
Authentication requirement.
Request schema.
Response schema.
Error responses.
Relevant parameters.

The generated OpenAPI documentation shall be treated as an implementation artifact and should remain consistent with this specification.

10. API Security Principles

The API shall:

Require authentication for protected operations.
Enforce authorization server-side.
Validate all incoming input.
Avoid exposing sensitive information.
Avoid logging credentials.
Protect authentication secrets.
Return safe error responses.
Prevent unauthorized direct API access.
Apply business rules consistently.
11. API Versioning

Version 1.0 shall use:

/api/v1

Breaking API changes should result in a new API version where compatibility cannot reasonably be maintained.

Backward-compatible additions may be introduced within the existing version where appropriate.

12. Pagination, Filtering and Sorting

Collection endpoints may support controlled:

Pagination.
Filtering.
Sorting.

Example:

GET /api/v1/employees?page=1&page_size=20

Example:

GET /api/v1/employees?status=available

Example:

GET /api/v1/employees?skill=Python

The exact supported query parameters shall be defined per endpoint.

13. API Traceability Principle

Each major API endpoint shall map to one or more approved SRS capabilities.

The traceability relationship shall be:

SRS Requirement
      │
      ▼
API Endpoint
      │
      ▼
Business Service
      │
      ▼
Database Operation
      │
      ▼
Frontend Workflow
      │
      ▼
Test Case

Endpoints shall not be added solely for architectural appearance.

14. API Baseline

The conventions defined in this section establish the Version 1.0 API baseline.

The following sections define the individual resource endpoints and their request/response contracts.

# 15. Employee APIs

## 15.1 List Employees

### Endpoint

```http
GET /api/v1/employees

15.2 Get Employee
Endpoint
GET /api/v1/employees/{employee_id}
Purpose

Returns detailed information for a specific employee.

Authentication

Required.

Successful Response
200 OK

The response may include:

Employee information.
Skills.
Certifications.
Availability.
Utilization.
Current allocations.
Errors
404 Not Found
403 Forbidden
15.3 Create Employee
Endpoint
POST /api/v1/employees
Purpose

Creates a new employee record.

Authentication

Required.

Request
{
  "employee_code": "EMP001",
  "name": "Example Employee",
  "email": "employee@example.com",
  "designation": "Software Engineer",
  "department": "Technology",
  "experience_years": 5,
  "availability_status": "available",
  "location": "Bangalore"
}
Successful Response
201 Created

The response shall contain the created employee identifier and relevant employee information.

Validation

The API shall validate:

Required fields.
Valid email format.
Valid experience value.
Valid availability status.
Duplicate employee identifiers.
Other applicable business rules.
15.4 Update Employee
Endpoint
PATCH /api/v1/employees/{employee_id}
Purpose

Updates permitted employee attributes.

Authentication

Required.

Successful Response
200 OK
Errors
404 Not Found
403 Forbidden
409 Conflict
422 Unprocessable Entity
15.5 Employee Search
Endpoint
GET /api/v1/employees/search
Purpose

Provides workforce search based on supported employee attributes.

Supported filters may include:

Skill.
Proficiency.
Experience.
Availability.
Utilization.
Designation.
Department.
Location.

Search results shall respect authorization rules.

16. Project APIs
16.1 List Projects
Endpoint
GET /api/v1/projects
Purpose

Returns projects accessible to the authenticated user.

Query Parameters

Supported filters may include:

Status.
Priority.
Client.
Start date.
End date.
Search text.
Successful Response
200 OK

Representative response:

{
  "items": [
    {
      "project_id": 201,
      "project_code": "PRJ001",
      "project_name": "Workforce Transformation",
      "client_name": "Example Client",
      "status": "active",
      "priority": "high"
    }
  ],
  "total": 1
}
16.2 Get Project
Endpoint
GET /api/v1/projects/{project_id}
Purpose

Returns project details.

Successful Response
200 OK

Project details may include:

Project information.
Staffing requirements.
Allocation summary.
Project status.
Relevant workforce information.
16.3 Create Project
Endpoint
POST /api/v1/projects
Request
{
  "project_code": "PRJ001",
  "project_name": "Workforce Transformation",
  "client_name": "Example Client",
  "description": "Example project",
  "start_date": "2026-09-01",
  "end_date": "2027-03-31",
  "status": "planned",
  "priority": "high"
}
Successful Response
201 Created
16.4 Update Project
Endpoint
PATCH /api/v1/projects/{project_id}
Purpose

Updates permitted project attributes.

Successful Response
200 OK
17. Skills APIs
17.1 List Skills
Endpoint
GET /api/v1/skills
Purpose

Returns standardized skills.

Query Parameters

Supported filters may include:

Category.
Status.
Search text.
Successful Response
200 OK
17.2 Get Skill
Endpoint
GET /api/v1/skills/{skill_id}
Purpose

Returns skill details.

17.3 Create Skill
Endpoint
POST /api/v1/skills
Request
{
  "skill_name": "Python",
  "category": "Programming",
  "description": "Python programming language",
  "status": "active"
}
Successful Response
201 Created
17.4 Update Skill
Endpoint
PATCH /api/v1/skills/{skill_id}
Successful Response
200 OK
17.5 Employee Skill Assignment
Endpoint
POST /api/v1/employees/{employee_id}/skills
Purpose

Associates a skill with an employee.

Request
{
  "skill_id": 10,
  "proficiency_level": "advanced",
  "years_experience": 4
}
Successful Response
201 Created
17.6 Update Employee Skill
Endpoint
PATCH /api/v1/employees/{employee_id}/skills/{skill_id}
Purpose

Updates the employee's skill relationship.

17.7 Employee Certifications
Endpoint
GET /api/v1/employees/{employee_id}/certifications
Purpose

Returns certifications associated with an employee.

17.8 Add Employee Certification
Endpoint
POST /api/v1/employees/{employee_id}/certifications
Request
{
  "certification_name": "Example Certification",
  "issuing_authority": "Example Authority",
  "issue_date": "2025-01-15",
  "expiry_date": "2028-01-15"
}
Successful Response
201 Created
18. Staffing Requirement APIs
18.1 List Staffing Requirements
Endpoint
GET /api/v1/staffing-requirements
Query Parameters

Supported filters may include:

Project.
Status.
Priority.
Role.
Start date.
End date.
18.2 Get Staffing Requirement
Endpoint
GET /api/v1/staffing-requirements/{staffing_requirement_id}
Purpose

Returns the complete staffing requirement.

The response may include:

Project.
Role.
Required quantity.
Required skills.
Required proficiency.
Required experience.
Required certifications.
Staffing dates.
Priority.
Status.
18.3 Create Staffing Requirement
Endpoint
POST /api/v1/staffing-requirements
Request
{
  "project_id": 201,
  "role_name": "Software Engineer",
  "required_quantity": 2,
  "required_experience": 4,
  "required_proficiency": "advanced",
  "start_date": "2026-09-01",
  "end_date": "2027-03-31",
  "priority": "high",
  "status": "open"
}

Required skills and certifications shall be represented through the approved relationship structures.

Successful Response
201 Created
18.4 Update Staffing Requirement
Endpoint
PATCH /api/v1/staffing-requirements/{staffing_requirement_id}
Purpose

Updates an existing staffing requirement.

Validation

The API shall validate:

Project existence.
Valid dates.
Required quantity.
Valid status.
Required experience.
Required proficiency.
Applicable project constraints.
18.5 Close Staffing Requirement
Endpoint
POST /api/v1/staffing-requirements/{staffing_requirement_id}/close
Purpose

Closes a staffing requirement when it no longer requires active staffing.

Successful Response
200 OK

The operation shall validate whether the requirement can be closed according to business rules.

19. Candidate Search APIs
19.1 Search Candidates
Endpoint
GET /api/v1/candidates/search
Purpose

Returns employees matching supported workforce search criteria.

Query Parameters

Possible filters include:

Parameter	Purpose
skill	Required skill
proficiency	Minimum proficiency
experience	Minimum experience
certification	Required certification
availability	Availability requirement
utilization_max	Maximum utilization
location	Workforce location
page	Page number
page_size	Page size
Successful Response
200 OK

Representative response:

{
  "items": [
    {
      "employee_id": 101,
      "name": "Example Employee",
      "matched_skills": [
        "Python",
        "FastAPI"
      ],
      "proficiency": "advanced",
      "experience_years": 5,
      "availability_status": "available",
      "utilization_percentage": 60
    }
  ],
  "total": 1
}
19.2 Candidate Search Rules

Candidate search shall:

Respect authorization.
Use authoritative workforce data.
Apply supplied filters.
Avoid returning restricted information.
Return no-match results when no employee satisfies the search criteria.

Candidate search shall not automatically create recommendations or allocations.

20. Recommendation APIs
20.1 Generate Recommendations
Endpoint
POST /api/v1/recommendations
Purpose

Generates ranked workforce recommendations for a staffing requirement.

Request
{
  "staffing_requirement_id": 301
}
Authentication

Required.

Processing Flow
Staffing Requirement
        │
        ▼
Eligibility Filtering
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
20.2 Recommendation Eligibility

Mandatory criteria shall be applied before scoring.

The recommendation service shall evaluate applicable:

Skills.
Proficiency.
Experience.
Certifications.
Availability.

Candidates failing mandatory requirements shall not be promoted through scoring.

20.3 Recommendation Response

Representative response:

{
  "staffing_requirement_id": 301,
  "recommendations": [
    {
      "employee_id": 101,
      "rank": 1,
      "score": 92,
      "eligibility_status": "eligible",
      "matched_skills": [
        "Python",
        "FastAPI"
      ],
      "reason": "Strong skill, experience and availability match"
    }
  ],
  "generated_at": "2026-08-08T18:30:00Z"
}
20.4 Recommendation No-Match Response

When no eligible candidates exist:

200 OK

Example:

{
  "staffing_requirement_id": 301,
  "recommendations": [],
  "message": "No eligible candidates found."
}

The system shall not fabricate candidate information.

20.5 Recommendation Detail
Endpoint
GET /api/v1/recommendations/{recommendation_id}
Purpose

Returns a stored recommendation result where recommendation persistence is enabled.

20.6 Recommendation and Allocation Boundary

The recommendation API shall never directly create a final allocation.

The workflow remains:

Recommendation
      ↓
Human Review
      ↓
Allocation API
21. API Baseline — Part 2

This section establishes the Version 1.0 API contracts for:

Employees.
Projects.
Skills.
Employee skills.
Certifications.
Staffing requirements.
Candidate search.
AI-assisted recommendations.

The next API sections shall define:

Resource allocation.
Resource release.
Dashboards.
Conversational Assistant.
Administration.
Audit.
API security and operational considerations.

15.2 Get Employee
Endpoint
GET /api/v1/employees/{employee_id}
Purpose

Returns detailed information for a specific employee.

Authentication

Required.

Successful Response
200 OK

The response may include:

Employee information.
Skills.
Certifications.
Availability.
Utilization.
Current allocations.
Errors
404 Not Found
403 Forbidden
15.3 Create Employee
Endpoint
POST /api/v1/employees
Purpose

Creates a new employee record.

Authentication

Required.

Request
{
  "employee_code": "EMP001",
  "name": "Example Employee",
  "email": "employee@example.com",
  "designation": "Software Engineer",
  "department": "Technology",
  "experience_years": 5,
  "availability_status": "available",
  "location": "Bangalore"
}
Successful Response
201 Created

The response shall contain the created employee identifier and relevant employee information.

Validation

The API shall validate:

Required fields.
Valid email format.
Valid experience value.
Valid availability status.
Duplicate employee identifiers.
Other applicable business rules.
15.4 Update Employee
Endpoint
PATCH /api/v1/employees/{employee_id}
Purpose

Updates permitted employee attributes.

Authentication

Required.

Successful Response
200 OK
Errors
404 Not Found
403 Forbidden
409 Conflict
422 Unprocessable Entity
15.5 Employee Search
Endpoint
GET /api/v1/employees/search
Purpose

Provides workforce search based on supported employee attributes.

Supported filters may include:

Skill.
Proficiency.
Experience.
Availability.
Utilization.
Designation.
Department.
Location.

Search results shall respect authorization rules.

16. Project APIs
16.1 List Projects
Endpoint
GET /api/v1/projects
Purpose

Returns projects accessible to the authenticated user.

Query Parameters

Supported filters may include:

Status.
Priority.
Client.
Start date.
End date.
Search text.
Successful Response
200 OK

Representative response:

{
  "items": [
    {
      "project_id": 201,
      "project_code": "PRJ001",
      "project_name": "Workforce Transformation",
      "client_name": "Example Client",
      "status": "active",
      "priority": "high"
    }
  ],
  "total": 1
}
16.2 Get Project
Endpoint
GET /api/v1/projects/{project_id}
Purpose

Returns project details.

Successful Response
200 OK

Project details may include:

Project information.
Staffing requirements.
Allocation summary.
Project status.
Relevant workforce information.
16.3 Create Project
Endpoint
POST /api/v1/projects
Request
{
  "project_code": "PRJ001",
  "project_name": "Workforce Transformation",
  "client_name": "Example Client",
  "description": "Example project",
  "start_date": "2026-09-01",
  "end_date": "2027-03-31",
  "status": "planned",
  "priority": "high"
}
Successful Response
201 Created
16.4 Update Project
Endpoint
PATCH /api/v1/projects/{project_id}
Purpose

Updates permitted project attributes.

Successful Response
200 OK
17. Skills APIs
17.1 List Skills
Endpoint
GET /api/v1/skills
Purpose

Returns standardized skills.

Query Parameters

Supported filters may include:

Category.
Status.
Search text.
Successful Response
200 OK
17.2 Get Skill
Endpoint
GET /api/v1/skills/{skill_id}
Purpose

Returns skill details.

17.3 Create Skill
Endpoint
POST /api/v1/skills
Request
{
  "skill_name": "Python",
  "category": "Programming",
  "description": "Python programming language",
  "status": "active"
}
Successful Response
201 Created
17.4 Update Skill
Endpoint
PATCH /api/v1/skills/{skill_id}
Successful Response
200 OK
17.5 Employee Skill Assignment
Endpoint
POST /api/v1/employees/{employee_id}/skills
Purpose

Associates a skill with an employee.

Request
{
  "skill_id": 10,
  "proficiency_level": "advanced",
  "years_experience": 4
}
Successful Response
201 Created
17.6 Update Employee Skill
Endpoint
PATCH /api/v1/employees/{employee_id}/skills/{skill_id}
Purpose

Updates the employee's skill relationship.

17.7 Employee Certifications
Endpoint
GET /api/v1/employees/{employee_id}/certifications
Purpose

Returns certifications associated with an employee.

17.8 Add Employee Certification
Endpoint
POST /api/v1/employees/{employee_id}/certifications
Request
{
  "certification_name": "Example Certification",
  "issuing_authority": "Example Authority",
  "issue_date": "2025-01-15",
  "expiry_date": "2028-01-15"
}
Successful Response
201 Created
18. Staffing Requirement APIs
18.1 List Staffing Requirements
Endpoint
GET /api/v1/staffing-requirements
Query Parameters

Supported filters may include:

Project.
Status.
Priority.
Role.
Start date.
End date.
18.2 Get Staffing Requirement
Endpoint
GET /api/v1/staffing-requirements/{staffing_requirement_id}
Purpose

Returns the complete staffing requirement.

The response may include:

Project.
Role.
Required quantity.
Required skills.
Required proficiency.
Required experience.
Required certifications.
Staffing dates.
Priority.
Status.
18.3 Create Staffing Requirement
Endpoint
POST /api/v1/staffing-requirements
Request
{
  "project_id": 201,
  "role_name": "Software Engineer",
  "required_quantity": 2,
  "required_experience": 4,
  "required_proficiency": "advanced",
  "start_date": "2026-09-01",
  "end_date": "2027-03-31",
  "priority": "high",
  "status": "open"
}

Required skills and certifications shall be represented through the approved relationship structures.

Successful Response
201 Created
18.4 Update Staffing Requirement
Endpoint
PATCH /api/v1/staffing-requirements/{staffing_requirement_id}
Purpose

Updates an existing staffing requirement.

Validation

The API shall validate:

Project existence.
Valid dates.
Required quantity.
Valid status.
Required experience.
Required proficiency.
Applicable project constraints.
18.5 Close Staffing Requirement
Endpoint
POST /api/v1/staffing-requirements/{staffing_requirement_id}/close
Purpose

Closes a staffing requirement when it no longer requires active staffing.

Successful Response
200 OK

The operation shall validate whether the requirement can be closed according to business rules.

19. Candidate Search APIs
19.1 Search Candidates
Endpoint
GET /api/v1/candidates/search
Purpose

Returns employees matching supported workforce search criteria.

Query Parameters

Possible filters include:

Parameter	Purpose
skill	Required skill
proficiency	Minimum proficiency
experience	Minimum experience
certification	Required certification
availability	Availability requirement
utilization_max	Maximum utilization
location	Workforce location
page	Page number
page_size	Page size
Successful Response
200 OK

Representative response:

{
  "items": [
    {
      "employee_id": 101,
      "name": "Example Employee",
      "matched_skills": [
        "Python",
        "FastAPI"
      ],
      "proficiency": "advanced",
      "experience_years": 5,
      "availability_status": "available",
      "utilization_percentage": 60
    }
  ],
  "total": 1
}
19.2 Candidate Search Rules

Candidate search shall:

Respect authorization.
Use authoritative workforce data.
Apply supplied filters.
Avoid returning restricted information.
Return no-match results when no employee satisfies the search criteria.

Candidate search shall not automatically create recommendations or allocations.

20. Recommendation APIs
20.1 Generate Recommendations
Endpoint
POST /api/v1/recommendations
Purpose

Generates ranked workforce recommendations for a staffing requirement.

Request
{
  "staffing_requirement_id": 301
}
Authentication

Required.

Processing Flow
Staffing Requirement
        │
        ▼
Eligibility Filtering
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
20.2 Recommendation Eligibility

Mandatory criteria shall be applied before scoring.

The recommendation service shall evaluate applicable:

Skills.
Proficiency.
Experience.
Certifications.
Availability.

Candidates failing mandatory requirements shall not be promoted through scoring.

20.3 Recommendation Response

Representative response:

{
  "staffing_requirement_id": 301,
  "recommendations": [
    {
      "employee_id": 101,
      "rank": 1,
      "score": 92,
      "eligibility_status": "eligible",
      "matched_skills": [
        "Python",
        "FastAPI"
      ],
      "reason": "Strong skill, experience and availability match"
    }
  ],
  "generated_at": "2026-08-08T18:30:00Z"
}
20.4 Recommendation No-Match Response

When no eligible candidates exist:

200 OK

Example:

{
  "staffing_requirement_id": 301,
  "recommendations": [],
  "message": "No eligible candidates found."
}

The system shall not fabricate candidate information.

20.5 Recommendation Detail
Endpoint
GET /api/v1/recommendations/{recommendation_id}
Purpose

Returns a stored recommendation result where recommendation persistence is enabled.

20.6 Recommendation and Allocation Boundary

The recommendation API shall never directly create a final allocation.

The workflow remains:

Recommendation
      ↓
Human Review
      ↓
Allocation API
21. API Baseline — Part 2

This section establishes the Version 1.0 API contracts for:

Employees.
Projects.
Skills.
Employee skills.
Certifications.
Staffing requirements.
Candidate search.
AI-assisted recommendations.

The next API sections shall define:

Resource allocation.
Resource release.
Dashboards.
Conversational Assistant.
Administration.
Audit.
API security and operational considerations.

# 22. Resource Allocation APIs

## 22.1 List Allocations

### Endpoint

```http
GET /api/v1/allocations

22.2 Get Allocation
Endpoint
GET /api/v1/allocations/{allocation_id}
Purpose

Returns details of a specific allocation.

Authentication

Required.

Successful Response
200 OK

The response may include:

Employee.
Project.
Staffing requirement.
Allocation percentage.
Start date.
End date.
Status.
Allocating user.
Creation timestamp.
22.3 Create Allocation
Endpoint
POST /api/v1/allocations
Purpose

Creates a final workforce allocation after authorized human selection.

Request
{
  "employee_id": 101,
  "project_id": 201,
  "staffing_requirement_id": 301,
  "allocation_percentage": 50,
  "start_date": "2026-09-01",
  "end_date": "2027-03-31"
}
Processing Flow
Selected Candidate
       │
       ▼
Allocation API
       │
       ▼
Authentication
       │
       ▼
Authorization
       │
       ▼
Current-State Validation
       │
       ├── Invalid ──► Reject
       │
       ▼
Transaction
       │
       ├── Create Allocation
       ├── Update Relevant Workforce State
       └── Create Audit Event
       │
       ▼
Allocation Response
Successful Response
201 Created
Validation

The API shall validate:

Employee existence.
Project existence.
Staffing requirement existence.
User authorization.
Employee availability.
Employee capacity.
Required skills.
Required proficiency.
Required experience.
Required certifications.
Date validity.
Allocation conflicts.
22.4 Allocation Conflict

If an allocation conflicts with the employee's current workforce state:

409 Conflict

Example:

{
  "error": {
    "code": "ALLOCATION_CONFLICT",
    "message": "The employee cannot be allocated for the requested period."
  }
}

The API shall not create the allocation when a blocking conflict exists.

22.5 Allocation Revalidation

The API shall revalidate the employee's current state at allocation time.

A previous recommendation shall not be treated as proof that the employee remains eligible.

The sequence shall remain:

Recommendation
      │
      ▼
User Selection
      │
      ▼
Current-State Revalidation
      │
      ▼
Allocation
23. Resource Release APIs
23.1 Release Resource
Endpoint
POST /api/v1/allocations/{allocation_id}/release
Purpose

Releases an employee from an active allocation.

Request
{
  "release_date": "2027-01-15",
  "reason": "Project requirement completed"
}
Successful Response
200 OK
Processing
Active Allocation
       │
       ▼
Release Request
       │
       ▼
Authorization
       │
       ▼
Release Validation
       │
       ▼
Update Allocation
       │
       ▼
Update Workforce Availability
       │
       ▼
Audit Event
23.2 Release Validation

The API shall validate:

Allocation existence.
Allocation status.
User authorization.
Valid release date.
Release date consistency with allocation dates.

An already released or inactive allocation shall not be released again.

24. Dashboard APIs
24.1 Workforce Dashboard
Endpoint
GET /api/v1/dashboard/workforce
Purpose

Returns workforce-level dashboard metrics accessible to the authenticated user.

Possible Metrics
Total employees.
Available employees.
Allocated employees.
Bench employees.
Average utilization.
Active allocations.
Open staffing requirements.
Successful Response
200 OK

Representative response:

{
  "total_employees": 250,
  "available_employees": 45,
  "allocated_employees": 205,
  "bench_employees": 45,
  "average_utilization": 78.4,
  "active_allocations": 220,
  "open_staffing_requirements": 18
}

The exact dashboard calculations shall follow the approved business rules.

24.2 Utilization Dashboard
Endpoint
GET /api/v1/dashboard/utilization
Purpose

Returns utilization-related workforce metrics.

Possible information includes:

Overall utilization.
Employee utilization.
Project utilization.
Allocation distribution.
24.3 Skills Dashboard
Endpoint
GET /api/v1/dashboard/skills
Purpose

Returns workforce skill distribution information.

Possible information includes:

Skill counts.
Proficiency distribution.
Certification coverage.
Skill availability.
24.4 Project Dashboard
Endpoint
GET /api/v1/dashboard/projects
Purpose

Returns project workforce and staffing information.

Possible information includes:

Active projects.
Staffing requirements.
Filled requirements.
Open requirements.
Allocation status.
24.5 Dashboard Authorization

Dashboard APIs shall apply the authenticated user's role and permissions before returning workforce information.

The API shall not expose executive or restricted workforce information to unauthorized roles.

25. Conversational Assistant API
25.1 Submit Query
Endpoint
POST /api/v1/assistant/query
Purpose

Processes an authorized workforce-management natural-language query.

Request
{
  "query": "Show available Python developers with more than 4 years of experience"
}
Processing Flow
Natural-Language Query
        │
        ▼
Authenticated User
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
Authorization
        │
        ▼
Workforce Query
        │
        ▼
Result Validation
        │
        ▼
Response Generation
Successful Response
200 OK

Representative response:

{
  "response": "2 available employees match the requested criteria.",
  "results": [
    {
      "employee_id": 101,
      "name": "Example Employee"
    }
  ]
}
25.2 Assistant Authorization

The Assistant shall use the same authorization context as the authenticated user.

Natural-language requests shall not bypass API permissions.

For example:

User lacks permission
       │
       ▼
Direct API request ──► Denied

Same user
       │
       ▼
Assistant request ──► Denied
25.3 Assistant No-Result Response

When no matching records exist:

{
  "response": "No matching employees were found.",
  "results": []
}

The Assistant shall not invent workforce records.

25.4 Assistant Unsupported Query

When the query is outside Version 1.0 scope:

{
  "response": "This request is outside the supported WorkforceIQ Assistant capabilities."
}

The Assistant shall not automatically behave as a general-purpose chatbot.

25.5 Assistant Error Handling

If the query cannot be interpreted safely or reliably, the API shall return a controlled response rather than fabricate an answer.

26. Administration APIs
26.1 List Users
Endpoint
GET /api/v1/admin/users
Purpose

Returns application users accessible to authorized administrators.

Authentication

Required.

Authorization

Administrative permission required.

26.2 Get User
Endpoint
GET /api/v1/admin/users/{user_id}
Purpose

Returns administrative user information.

Sensitive authentication information such as password hashes shall never be returned through the API.

26.3 Create User
Endpoint
POST /api/v1/admin/users
Purpose

Creates a WorkforceIQ user account.

Request
{
  "username": "user@example.com",
  "email": "user@example.com",
  "employee_id": 101,
  "role_ids": [2],
  "status": "active"
}

The implementation shall securely generate or process credentials without exposing passwords in API responses.

26.4 Update User
Endpoint
PATCH /api/v1/admin/users/{user_id}
Purpose

Updates permitted account attributes, roles, or status.

Administrative authorization is required.

26.5 List Roles
Endpoint
GET /api/v1/admin/roles
Purpose

Returns available application roles.

26.6 List Permissions
Endpoint
GET /api/v1/admin/permissions
Purpose

Returns available application permissions for authorized administrators.

26.7 Role-Permission Management
Endpoint
POST /api/v1/admin/roles/{role_id}/permissions
Purpose

Associates a permission with an application role.

Request
{
  "permission_id": 10
}

The operation shall require administrative authorization.

27. Audit APIs
27.1 List Audit Events
Endpoint
GET /api/v1/audit/events
Purpose

Returns audit events available to authorized users.

Query Parameters

Possible filters include:

user_id
action
entity_type
entity_id
start_date
end_date
page
page_size
Successful Response
200 OK

Representative response:

{
  "items": [
    {
      "audit_event_id": 9001,
      "user_id": 1,
      "action": "ALLOCATION_CREATED",
      "entity_type": "allocation",
      "entity_id": 501,
      "result": "success",
      "event_timestamp": "2026-08-08T18:30:00Z"
    }
  ],
  "total": 1
}
27.2 Audit Access Control

Audit information shall be restricted to authorized roles.

The API shall not expose audit information to users who do not have appropriate permissions.

28. API Error Handling
28.1 Standard Error Categories

The API shall use consistent error categories:

VALIDATION_ERROR
AUTHENTICATION_ERROR
AUTHORIZATION_ERROR
NOT_FOUND
CONFLICT
BUSINESS_RULE_ERROR
INTERNAL_ERROR
28.2 Validation Error

Example:

{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request.",
    "details": [
      {
        "field": "allocation_percentage",
        "message": "Value must be between the supported limits."
      }
    ]
  }
}
28.3 Business Rule Error

Example:

{
  "error": {
    "code": "BUSINESS_RULE_ERROR",
    "message": "The employee does not satisfy the required skill criteria."
  }
}
28.4 Internal Error

Unexpected errors shall return a safe response:

{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An unexpected error occurred."
  }
}

Internal implementation details shall be recorded in controlled logs rather than returned to the client.

29. API Security Controls
29.1 Authentication

Protected endpoints shall require valid authentication.

29.2 Authorization

Each protected operation shall verify the user's role or permission.

29.3 Input Validation

All externally supplied input shall be validated before processing.

29.4 Sensitive Data

The API shall not return:

Password hashes.
Authentication secrets.
JWT signing secrets.
Internal database credentials.
Unnecessary sensitive employee information.
29.5 Error Security

Error responses shall not reveal:

Stack traces.
SQL statements.
Database credentials.
Internal filesystem paths.
Authentication secrets.
29.6 Audit

Material business and security operations shall generate appropriate audit events.

30. API Performance Considerations

The API shall be designed to support the Version 1.0 performance expectations defined in the SRS.

The primary target is:

Typical API operations: responsive under expected local workload
Recommendation generation: approximately ≤ 5 seconds
Supported Assistant queries: approximately ≤ 5 seconds

Performance shall be evaluated using a representative local dataset during testing.

The API shall not claim enterprise-scale performance guarantees for Version 1.0.

31. API Maintainability

The API implementation shall:

Use consistent naming.
Use reusable schemas.
Avoid duplicated business logic.
Separate routing from business services.
Use centralized error handling where practical.
Maintain OpenAPI documentation.
Keep authentication and authorization reusable.
Maintain traceability to requirements.
32. API Change Management

Material API changes shall follow the project requirements change-management process.

Changes affecting:

Endpoint paths.
Request contracts.
Response contracts.
Authentication.
Authorization.
Business behavior.

shall be assessed for compatibility impact.

33. API Traceability

The API implementation shall maintain traceability across:

SRS Requirement
      │
      ▼
API Endpoint
      │
      ▼
Service
      │
      ▼
Database
      │
      ▼
Frontend
      │
      ▼
Test Case

The API Specification shall be updated if approved requirements materially change.

34. API Completion Criteria

The API Specification shall be considered complete when:

API conventions are defined.
Authentication is defined.
Authorization is defined.
Common request/response structures are defined.
Error handling is defined.
Employee APIs are defined.
Project APIs are defined.
Skills APIs are defined.
Staffing Requirement APIs are defined.
Candidate Search APIs are defined.
Recommendation APIs are defined.
Allocation APIs are defined.
Resource Release APIs are defined.
Dashboard APIs are defined.
Conversational Assistant API is defined.
Administration APIs are defined.
Audit APIs are defined.
Security requirements are defined.
Performance considerations are defined.
Traceability is defined.
The API contract is ready to support frontend implementation.
35. API Baseline

The API Specification establishes the Version 1.0 REST API baseline for WorkforceIQ.

The API provides the controlled interface between the React frontend and FastAPI backend while enforcing authentication, authorization, validation, business rules, and safe error handling.

The API shall remain aligned with the approved SRS, System Design, and Database Design.

Material changes identified during implementation shall be evaluated through the project's change-management process.

36. End of API Specification

This document defines the Version 1.0 API contract required to support WorkforceIQ's approved workforce-management capabilities.

The next project artifact shall define the Version 1.0 user interface and user experience specification for the React frontend.