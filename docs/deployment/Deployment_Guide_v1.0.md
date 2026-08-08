# WorkforceIQ

# Deployment Guide

---

## Document Information

| Item | Details |
|------|---------|
| Product Name | WorkforceIQ |
| Document Type | Deployment Guide |
| Version | 1.0 |
| Status | Draft |
| Project Type | AI-Powered Workforce Management Platform |
| Methodology | Agile Scrum |
| Prepared By | Nitish Malik |
| Language | English |
| Repository | AI-Workforce-Intelligence-Platform |
| Requirements Reference | WorkforceIQ SRS Version 1.0 |
| Business Reference | WorkforceIQ BRD/PRD Version 1.0 |
| System Design Reference | WorkforceIQ System Design Version 1.0 |
| Database Reference | WorkforceIQ Database Design Version 1.0 |
| API Reference | WorkforceIQ API Specification Version 1.0 |
| UI Reference | WorkforceIQ UI/UX Specification Version 1.0 |
| Test Reference | WorkforceIQ Test Strategy and Test Plan Version 1.0 |
| Deployment Scope | Version 1.0 Local / Development Deployment |

---

# 1. Introduction

## 1.1 Purpose

This Deployment Guide defines the Version 1.0 deployment and operational setup process for WorkforceIQ.

The guide provides the steps required to:

- Prepare the development environment.
- Configure the backend.
- Configure the frontend.
- Initialize the database.
- Configure environment variables.
- Start the application.
- Verify that the application is functioning.
- Troubleshoot common startup issues.
- Shut down the application safely.

---

## 1.2 Deployment Scope

Version 1.0 deployment is primarily focused on local development and demonstration.

The expected deployment architecture is:

```text
Developer Machine
        │
        ├───────────────────────┐
        │                       │
        ▼                       ▼
React Frontend              FastAPI Backend
        │                       │
        │                       ▼
        │                  SQLite Database
        │
        └──────── HTTP/API ─────┘


2. Deployment Objectives

The deployment process shall establish a repeatable environment in which:

The React frontend can be started.
The FastAPI backend can be started.
The database can be initialized.
Required configuration can be supplied.
Frontend and backend can communicate.
Authentication can be exercised.
Core APIs can be tested.
Core UI workflows can be demonstrated.
Test data can be loaded where required.
3. Deployment Prerequisites
3.1 Hardware

The development machine should have sufficient resources to run:

React development server.
FastAPI application.
SQLite.
Development/testing tools.

The exact minimum hardware specification is not considered a Version 1.0 release constraint.

3.2 Operating System

The deployment guide primarily assumes a Windows development environment.

Equivalent commands may be used on other operating systems where applicable.

3.3 Required Software

The development environment should provide:

Git.
Python.
Node.js.
npm.
A supported web browser.
Code editor/IDE.
PowerShell or equivalent terminal.
3.4 Repository

The project shall be obtained from the approved Git repository.

Expected project structure:

AI-Workforce-Intelligence-Platform/
│
├── backend/
├── frontend/
├── docs/
├── data/
├── tests/
├── README.md
└── ...

The exact structure may evolve during implementation.

4. Source Code Setup
4.1 Clone Repository

From the desired development directory:

git clone <repository-url>

Navigate to the project:

cd AI-Workforce-Intelligence-Platform
4.2 Verify Repository

Verify that the project structure is available:

Get-ChildItem

Expected major directories include:

backend
frontend
docs

Additional directories may exist depending on the implementation.

5. Backend Deployment
5.1 Navigate to Backend
cd backend
5.2 Create Python Virtual Environment

Create a dedicated virtual environment:

python -m venv .venv

Activate it:

.\.venv\Scripts\Activate.ps1

After activation, the terminal should indicate that the virtual environment is active.

5.3 Install Backend Dependencies

If the project contains requirements.txt:

pip install -r requirements.txt

If dependency management changes during implementation, the final command shall be updated accordingly.

5.4 Backend Environment Variables

Backend configuration shall be supplied through environment variables or an approved configuration mechanism.

Typical configuration categories include:

DATABASE_URL
JWT_SECRET_KEY
JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES
CORS_ORIGINS

Additional configuration may be introduced during implementation.

5.5 Environment File

Where .env is used, a local development file may contain configuration such as:

DATABASE_URL=sqlite:///./workforceiq.db
JWT_SECRET_KEY=<development-secret>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
CORS_ORIGINS=http://localhost:5173

Development secrets shall not be committed to Git.

A safe example configuration file may be maintained separately, such as:

.env.example
6. Database Initialization
6.1 Database

Version 1.0 local deployment shall use SQLite unless the implementation is explicitly changed.

Expected development database:

workforceiq.db

The exact filename may be finalized during implementation.

6.2 Database Creation

The backend shall initialize the database using the project's approved database initialization or migration process.

The exact command shall depend on the implementation.

Examples may include:

alembic upgrade head

or an application-specific initialization command.

The final implementation command shall be documented once the database layer is completed.

6.3 Database Validation

After initialization, verify that:

The database exists.
Required tables exist.
Relationships are valid.
Required seed/reference data exists where applicable.
7. Seed / Test Data
7.1 Purpose

Representative test data shall be available for development and testing.

The dataset should include:

Employees.
Skills.
Certifications.
Projects.
Staffing requirements.
Allocations.
Workforce availability states.
7.2 Recommendation Test Data

The dataset should include candidates representing:

Strong matches.
Partial matches.
Mandatory-criteria failures.
Availability conflicts.
Certification mismatches.
Experience mismatches.
No-match scenarios.

This allows the recommendation workflow to be demonstrated and tested realistically.

7.3 Development Data

Development/test data shall not contain unnecessary production or sensitive personal information.

8. Start Backend

From the backend directory with the virtual environment activated:

uvicorn app.main:app --reload

The exact module path may change according to the final backend structure.

Expected result:

Uvicorn running on http://127.0.0.1:8000
8.1 Backend Verification

Open the API documentation endpoint if enabled:

http://127.0.0.1:8000/docs

Verify that:

The application starts.
API documentation loads.
Authentication endpoints are available.
Core API endpoints are visible.
9. Frontend Deployment
9.1 Navigate to Frontend

Open a separate terminal and navigate to:

cd AI-Workforce-Intelligence-Platform
cd frontend
9.2 Install Dependencies

Run:

npm install

This installs the frontend dependencies defined by the project.

9.3 Frontend Environment Variables

Where required, configure the backend API base URL.

Example:

VITE_API_BASE_URL=http://127.0.0.1:8000

The exact environment-variable name shall follow the implementation.

9.4 Start Frontend

Run:

npm run dev

Expected result:

Local: http://localhost:5173/

The exact port may differ if configured otherwise.

10. Frontend-to-Backend Connectivity

The frontend shall communicate with the FastAPI backend through the configured API base URL.

Expected flow:

Browser
   │
   ▼
React Frontend
   │
   ▼
API Base URL
   │
   ▼
FastAPI Backend
   │
   ▼
SQLite Database
10.1 CORS

The backend shall permit requests from the configured development frontend origin.

For example:

http://localhost:5173

CORS configuration shall not unnecessarily allow unrestricted origins in environments where tighter configuration is appropriate.

11. Initial Deployment Verification

After starting both frontend and backend:

Step 1

Open the frontend in a browser.

Step 2

Verify the login screen appears.

Step 3

Authenticate using a valid development/test account.

Step 4

Verify the dashboard loads.

Step 5

Open the Employees module.

Step 6

Open the Projects module.

Step 7

Open Staffing Requirements.

Step 8

Perform a candidate search.

Step 9

Generate a recommendation using valid test data.

Step 10

Verify that final allocation requires an authorized human action.

12. Basic Deployment Smoke Test

The deployment shall pass the basic smoke test when:

Backend Starts
     ↓
API Documentation Loads
     ↓
Frontend Starts
     ↓
Login Works
     ↓
Dashboard Loads
     ↓
Employee Data Loads
     ↓
Project Data Loads
     ↓
Staffing Data Loads
     ↓
Recommendation Workflow Loads
     ↓
Allocation Workflow Can Be Reached

Failure of a critical step shall block further deployment validation until the issue is investigated.

13. Deployment Environment Separation

Version 1.0 should distinguish between:

Development
    │
    ├── Local database
    ├── Development secrets
    └── Test data

Testing
    │
    ├── Controlled test configuration
    ├── Test dataset
    └── Test execution

Production
    │
    └── Future deployment scope

Production deployment shall not reuse development credentials or test data.

14. Configuration Management

Configuration shall be externalized where practical.

The source code repository shall not contain:

Production secrets.
Passwords.
Private API keys.
JWT signing secrets.
Database credentials.

Configuration templates may be committed when they contain placeholder values only.

15. Git and Deployment Files

The repository should exclude local runtime artifacts.

Examples include:

.venv/
node_modules/
.env
*.db
__pycache__/

The final .gitignore shall reflect the actual project implementation.

16. Deployment Troubleshooting
16.1 Backend Does Not Start

Check:

Python installation.
Virtual environment activation.
Dependencies.
Environment variables.
Database configuration.
Application import path.
Port availability.
16.2 Frontend Does Not Start

Check:

Node.js installation.
npm installation.
node_modules.
Dependency installation.
Environment variables.
Port availability.
16.3 Frontend Cannot Reach Backend

Check:

Backend is running.
API base URL is correct.
Backend port is correct.
CORS configuration is correct.
Browser developer-console errors.
Network/API response status.
16.4 Login Fails

Check:

Backend authentication endpoint.
Test user existence.
Password configuration.
Database connectivity.
JWT configuration.
Browser network requests.
16.5 Database Errors

Check:

Database file/path.
Database initialization.
Migration state.
Connection configuration.
Required tables.
File permissions.
17. Shutdown Procedure
17.1 Stop Frontend

In the frontend terminal:

Ctrl + C
17.2 Stop Backend

In the backend terminal:

Ctrl + C
17.3 Deactivate Virtual Environment
deactivate
18. Local Restart Procedure

A normal development restart should follow:

Open Terminal
     ↓
Navigate to backend
     ↓
Activate .venv
     ↓
Start FastAPI
     ↓
Open second terminal
     ↓
Navigate to frontend
     ↓
Start React
     ↓
Open browser
     ↓
Verify application
19. Deployment Baseline — Part 1

This section establishes the Version 1.0 deployment baseline for:

Local environment preparation.
Repository setup.
Backend setup.
Database initialization.
Test data.
Frontend setup.
Frontend/backend connectivity.
Smoke testing.
Configuration management.
Basic troubleshooting.
Application shutdown.

The next sections shall define:

Security configuration.
Backup and recovery considerations.
Deployment validation.
Operational checks.
Future production deployment considerations.
Deployment completion criteria.

# 20. Security Configuration

## 20.1 Development Secrets

Development secrets shall be stored outside the committed source code.

Examples include:

- JWT signing secret.
- Database credentials where applicable.
- External service credentials where introduced.

Development secrets shall not be committed to Git.

---

## 20.2 JWT Configuration

The backend shall use the configured JWT settings for authenticated sessions.

Typical configuration includes:

```text
JWT_SECRET_KEY
JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES

20.3 CORS Configuration

CORS shall be configured to permit only the frontend origins required by the environment.

Development example:

http://localhost:5173

Broad unrestricted CORS configuration should not be used as a production default.

20.4 Authentication Verification

After deployment, verify:

Login with valid credentials succeeds.
Invalid credentials are rejected.
Protected endpoints reject unauthenticated requests.
Authorized users can access permitted functionality.
Unauthorized users cannot access restricted functionality.
Logout/session handling works as designed.
21. Database Backup and Recovery
21.1 Development Backup

For the SQLite development database, a backup may be created by copying the database file while the application is stopped or using an appropriate SQLite backup mechanism.

Example conceptual backup:

workforceiq.db
      ↓
backup/
      ↓
workforceiq_<date>.db
21.2 Backup Scope

A development backup may contain:

Employee records.
Skill records.
Project records.
Staffing requirements.
Allocations.
Recommendations where persisted.
Audit records.
Reference data.

Backups containing sensitive information shall be protected appropriately.

21.3 Recovery

To recover a development database:

Stop the backend.
Preserve the damaged database file if investigation is required.
Restore the approved backup.
Verify database integrity.
Start the backend.
Perform the deployment smoke test.
Confirm critical application workflows.
21.4 Production Recovery

Production-grade backup frequency, retention, disaster recovery, replication, and recovery-point objectives are outside the Version 1.0 local deployment scope.

They shall be defined before any production deployment.

22. Deployment Validation
22.1 Application Validation

After deployment, validate:

Frontend availability.
Backend availability.
Database connectivity.
Authentication.
Authorization.
Employee retrieval.
Project retrieval.
Staffing requirement retrieval.
Candidate search.
Recommendation generation.
Allocation workflow.
Resource release.
Assistant workflow.
Audit behavior.
22.2 API Validation

The API shall be checked through the generated OpenAPI documentation and/or API testing tools.

Minimum validation shall include:

Authentication
Employees
Projects
Skills
Staffing Requirements
Candidate Search
Recommendations
Allocations
Resource Release
Dashboard
Assistant
Administration
Audit
22.3 Frontend Validation

The frontend shall be checked for:

Navigation.
Page loading.
Form rendering.
API integration.
Validation messages.
Loading states.
Empty states.
Error states.
Role-based visibility.
Core workforce workflows.
23. Deployment Smoke Test Checklist

The following checklist may be used after each meaningful local deployment.

Check	Expected Result	Status
Backend starts	FastAPI starts without blocking errors	☐
API docs	OpenAPI documentation loads	☐
Database	Database is accessible	☐
Frontend starts	React application loads	☐
Login	Valid user can authenticate	☐
Authorization	Restricted action is blocked	☐
Dashboard	Metrics/data load	☐
Employees	Employee list loads	☐
Projects	Project list loads	☐
Staffing	Requirements load	☐
Candidate Search	Search returns expected data	☐
Recommendations	Recommendations generate	☐
Allocation	Authorized allocation succeeds	☐
Conflict Handling	Invalid allocation is rejected	☐
Release	Resource release works	☐
Assistant	Supported query works	☐
Audit	Material action is recorded	☐

A failed critical check shall be investigated before considering the deployment stable.

24. Operational Checks
24.1 Backend Health

Where a health endpoint is implemented, it should be used to verify backend availability.

Example:

GET /health

The exact endpoint shall follow the final implementation.

24.2 Database Health

Verify that:

The database is accessible.
Required tables exist.
Queries execute successfully.
No unexpected database errors are present.
24.3 Application Logs

Application logs should be checked for:

Startup failures.
Database connection errors.
Authentication errors.
Unexpected exceptions.
API failures.

Logs shall not expose passwords, secrets, or other sensitive credentials.

25. Deployment Troubleshooting Matrix
Problem	Likely Cause	Initial Action
Backend fails to start	Dependency/configuration issue	Check Python environment and logs
Port already in use	Another process uses the port	Identify/stop process or use configured port
Database unavailable	Incorrect path/configuration	Verify database configuration
Frontend fails to start	npm/dependency issue	Run dependency installation and inspect output
API requests fail	Backend/CORS/API URL issue	Verify backend and frontend configuration
Login fails	User/configuration/database issue	Verify test account and backend logs
Empty dashboard	Missing/incorrect test data	Verify database seed data
Recommendations empty	No eligible candidates	Verify requirement and test dataset
Allocation rejected	Business-rule conflict	Inspect validation response
Assistant fails	API/model/service issue	Inspect backend logs and request response
26. Development Environment Reset

When a clean local environment is required:

Stop Frontend
      ↓
Stop Backend
      ↓
Deactivate Virtual Environment
      ↓
Review Local Configuration
      ↓
Recreate Virtual Environment if required
      ↓
Reinstall Dependencies
      ↓
Reinitialize Database if required
      ↓
Load Test Data
      ↓
Start Backend
      ↓
Start Frontend
      ↓
Run Smoke Test

A database reset shall only be performed when existing local data can safely be discarded or has been backed up.

27. Dependency Management
27.1 Backend

Python dependencies shall be captured in the project's approved dependency file.

Example:

requirements.txt

The exact dependency-management mechanism may evolve during implementation.

27.2 Frontend

Frontend dependencies shall be maintained through the project's Node/npm dependency files.

Expected files include:

package.json
package-lock.json

The lock file should be committed where appropriate to provide repeatable dependency installation.

27.3 Dependency Updates

Dependencies should not be upgraded arbitrarily during implementation.

Updates shall be evaluated for:

Compatibility.
Security.
Breaking changes.
Test impact.
28. Deployment Reproducibility

A developer starting from a clean repository should be able to reproduce the Version 1.0 development environment using:

Repository
    +
Documented prerequisites
    +
Dependency installation
    +
Environment configuration
    +
Database initialization
    +
Test data
    +
Startup commands

The deployment guide shall be updated if implementation changes make the documented setup inaccurate.

29. Future Production Deployment
29.1 Production Scope

Production deployment is outside the primary Version 1.0 local deployment scope.

Before production deployment, the architecture should be reassessed for:

Production database technology.
HTTPS/TLS.
Secret management.
Reverse proxy.
Application process management.
Database backup.
Monitoring.
Logging.
Scaling.
Disaster recovery.
Network security.
Infrastructure availability.
29.2 Production Architecture Direction

A future production architecture may evolve toward:

Internet / Corporate Network
            │
            ▼
       Reverse Proxy
            │
      ┌─────┴─────┐
      ▼           ▼
   Frontend     Backend
                   │
                   ▼
             Production DB
                   │
          ┌────────┴────────┐
          ▼                 ▼
       Logging          Monitoring

This is a future deployment direction and not a Version 1.0 implementation requirement.

30. Environment Comparison
Area	Development	Future Production
Frontend	Local React server	Production web hosting
Backend	Local FastAPI/Uvicorn	Managed application process
Database	SQLite	Production-grade DB if required
Secrets	Local environment configuration	Secure secret management
HTTPS	Optional/local	Required
Data	Test/development data	Controlled production data
Monitoring	Basic logs	Monitoring and alerting
Backup	Manual/local	Automated policy
Scaling	Not required	Designed as needed
31. Deployment Security Checklist

Before any environment is considered ready, verify:

 Secrets are not committed.
 Development credentials are not reused for production.
 Authentication is enabled.
 Authorization is enforced.
 CORS is appropriately restricted.
 Sensitive API responses are protected.
 Error responses do not expose internal details.
 Logs do not contain credentials.
 Database access is appropriately restricted.
 Backup handling is understood.
 Test data is not accidentally used as production data.
32. Deployment Completion Criteria

The Version 1.0 local deployment shall be considered complete when:

Required prerequisites are installed.
Repository is available.
Backend dependencies are installed.
Frontend dependencies are installed.
Environment configuration is available.
Database is initialized.
Test/reference data is available.
Backend starts successfully.
Frontend starts successfully.
Frontend can communicate with backend.
Authentication works.
Authorization works.
Core API operations work.
Core UI workflows work.
Recommendation workflow can be executed.
Allocation workflow can be executed.
Resource release can be executed.
Assistant workflow can be exercised.
Audit behavior can be verified.
Deployment smoke testing passes.
33. Deployment Runbook
33.1 Standard Startup
1. Open project directory
2. Start backend environment
3. Activate Python virtual environment
4. Start FastAPI
5. Open second terminal
6. Navigate to frontend
7. Start React application
8. Open browser
9. Authenticate
10. Run smoke checks
33.2 Standard Shutdown
1. Stop frontend
2. Stop backend
3. Deactivate virtual environment
4. Confirm no required process remains active
33.3 Post-Change Validation

After material implementation changes:

Code Change
    ↓
Application Start
    ↓
Relevant Tests
    ↓
Smoke Test
    ↓
Affected Workflow Validation
    ↓
Regression Testing
34. Deployment and Documentation Alignment

The deployment process shall remain aligned with:

System Design.
Database Design.
API Specification.
UI/UX Specification.
Test Strategy.

If implementation decisions materially change the deployment architecture, this document shall be updated during the final documentation reconciliation.

35. Deployment Baseline

This Deployment Guide establishes the Version 1.0 local/development deployment baseline for WorkforceIQ.

The baseline includes:

Source Repository
       ↓
Backend Environment
       ↓
Database
       ↓
FastAPI API
       ↓
React Frontend
       ↓
Authentication
       ↓
Workforce Workflows
       ↓
Testing / Smoke Validation

The guide deliberately avoids claiming production-readiness for infrastructure that has not yet been implemented or validated.

36. End of Deployment Guide

This document defines the Version 1.0 deployment, startup, validation, troubleshooting, security, backup, and operational baseline for WorkforceIQ.

All project documentation artifacts are now created.

The next activity is the final cross-document reconciliation before the documentation baseline is committed and pushed to the repository.

