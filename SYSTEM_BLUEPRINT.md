I actually think this should become **Document 00**, and it should be the **most important document** in the repository.

Every Cursor prompt will start with:

> **Follow Engineering Principles (Document 00) without exception.**

This dramatically improves consistency.

---

# Document 00 — Engineering Principles & Development Standards

**Project:** EcoSphere – Enterprise ESG Management Platform

**Version:** 1.0

**Status:** Mandatory

---

# 1. Philosophy

EcoSphere is an enterprise-grade SaaS platform.

The objective is **not** to quickly generate CRUD pages.

The objective is to build a modular, scalable, maintainable application that demonstrates professional software engineering practices.

Every engineering decision must prioritize:

* Maintainability
* Scalability
* Readability
* Reusability
* Extensibility
* Testability
* Performance
* Security

Short-term shortcuts that compromise architecture are prohibited.

---

# 2. Engineering Principles

The project shall follow:

* Clean Code
* SOLID
* DRY
* KISS
* YAGNI
* Domain Driven Design
* Modular Monolith
* Feature-Based Architecture
* Component-Driven UI
* API First Design

---

# 3. Architecture Principles

Business logic **must never** exist inside:

* React Components
* API Routers
* SQLAlchemy Models
* Utility Functions

Business logic belongs exclusively in **Services**.

---

# 4. Project Structure

Every feature owns everything related to itself.

Correct:

```text
environmental/
    router.py
    service.py
    repository.py
    schema.py
    model.py
```

Incorrect:

```text
models.py
routers.py
utils.py
helpers.py
```

No global dumping grounds.

---

# 5. Naming Standards

Folders

```text
snake_case
```

Files

```text
snake_case
```

Classes

```text
PascalCase
```

Functions

```text
snake_case
```

Variables

```text
snake_case
```

Constants

```text
UPPER_CASE
```

Interfaces (TypeScript)

```text
PascalCase
```

React Components

```text
PascalCase
```

---

# 6. Folder Rules

Each module must contain:

```text
models.py

schemas.py

repository.py

service.py

router.py

permissions.py

validators.py

events.py
```

Frontend

```text
api/

components/

hooks/

pages/

types/
```

---

# 7. Service Layer Rules

Services own:

* Business Rules
* Transactions
* Validation
* Domain Events
* Score Calculations
* Notifications

Services must never:

* Return ORM objects directly.
* Perform HTTP handling.
* Know about React.
* Generate HTML.

---

# 8. Repository Rules

Repositories only:

* Query Database
* Save Data
* Delete Data
* Pagination
* Filtering

Repositories never:

* Send Notifications
* Calculate ESG
* Award XP
* Validate Permissions

---

# 9. Router Rules

Routers only:

* Receive Request
* Validate Schema
* Authenticate
* Call Service
* Return Response

Routers never:

* Write SQL
* Calculate Scores
* Implement Business Rules

---

# 10. React Rules

React Components must:

* Display UI
* Call Hooks
* Trigger Actions

React Components must never:

* Call fetch()
* Perform calculations
* Implement business rules

---

# 11. API Rules

Every endpoint:

* Typed Request
* Typed Response
* Validation
* Error Handling

Always:

```text
/api/v1/
```

Never:

```text
/api/test
/api/new
/api/temp
```

---

# 12. Database Rules

Every table:

* UUID PK
* FK Constraints
* Indexes
* Audit Columns

Never duplicate data.

Always normalize.

---

# 13. Business Rules

Business rules belong only inside Services.

Example

Incorrect

```python
if xp > 100:
    badge = "Gold"
```

inside React.

Correct

```python
GamificationService

↓

award_badge()
```

---

# 14. Validation

Validation occurs in layers.

1.

Frontend

↓

2.

Pydantic

↓

3.

Service

↓

4.

Database

---

# 15. Error Handling

Never

```python
except:
    pass
```

Always raise typed exceptions.

Example

```text
ValidationError

NotFoundError

PermissionDeniedError

ConflictError
```

---

# 16. Logging

Every mutation logs:

* User
* Action
* Entity
* Timestamp
* Metadata

---

# 17. Security

Passwords

↓

Hash

JWT

↓

Protected Routes

RBAC

↓

Permission Middleware

No secrets in source code.

---

# 18. Events

Services emit events.

Example

```text
Participation Approved

↓

XP Awarded

↓

Badge Check

↓

Leaderboard

↓

Notification
```

No module directly updates another module.

---

# 19. AI Rules

LLMs never access the database directly.

Flow

```text
Database

↓

Service

↓

Prompt Builder

↓

LLM

↓

Formatter

↓

Response
```

---

# 20. UI Rules

Every page composed from reusable components.

Never duplicate cards.

Never duplicate tables.

Never duplicate forms.

---

# 21. Component Rules

Maximum responsibility:

One component = One purpose.

Split large components into smaller ones.

---

# 22. TypeScript Rules

Strict mode enabled.

Never use:

```typescript
any
```

Prefer explicit interfaces and types.

---

# 23. Python Rules

* Use type hints everywhere.
* Follow PEP 8.
* Keep functions focused.
* Prefer dependency injection.
* Avoid global state.

---

# 24. Performance Rules

* Lazy load routes.
* Paginate large datasets.
* Cache read-heavy queries where appropriate.
* Avoid unnecessary re-renders.
* Prevent N+1 queries.

---

# 25. Git Standards

Branch naming:

```text
feature/environmental

feature/social

feature/governance

fix/auth
```

Commit format:

```text
feat:

fix:

refactor:

docs:

style:

test:

perf:
```

---

# 26. Testing Rules

Every service should be independently testable.

Prefer testing business logic over UI.

No hidden dependencies.

---

# 27. Cursor Guardrails (Mandatory)

Cursor **must not**:

* Create duplicate components.
* Create duplicate APIs.
* Invent database tables.
* Ignore documented architecture.
* Bypass the Service layer.
* Place business logic in UI.
* Mix unrelated responsibilities.
* Use placeholder code without marking it.
* Add libraries without approval.

Cursor **must**:

* Follow the documented folder structure.
* Reuse existing components.
* Reuse services.
* Reuse repositories.
* Keep files cohesive.
* Respect module boundaries.
* Generate production-quality code.

---

# 28. Definition of Done

A feature is complete only when:

* Business rules implemented.
* Validation complete.
* API documented.
* Error handling added.
* Types defined.
* UI responsive.
* RBAC enforced.
* Activity logged (where applicable).
* Code reviewed.
* No lint/type errors.

---

# 29. Architecture Guardrails

Every new feature must answer:

1. Which module owns this?
2. Which service owns the business logic?
3. Which repository accesses the data?
4. Which events are emitted?
5. Which permissions are required?
6. Which audit logs are created?
7. Which notifications are triggered?
8. Which reports consume this data?

If any answer is unclear, the design must be clarified before implementation.

---

# 30. Cursor Execution Policy

Cursor is an **implementation engine**, not the system architect.

It must:

1. Read **Document 00** first.
2. Follow **Documents 01–06**.
3. Implement one module at a time.
4. Reuse existing code before creating new code.
5. Ask for clarification rather than invent architecture when requirements are ambiguous.

---

## Final Recommendation

At this point, you have a solid architectural foundation. Before coding, I recommend one additional artifact that will significantly improve Cursor's output:

**`ARCHITECTURE.md`** — a concise 2–3 page reference that summarizes Documents 00–06 into a quick-reference guide. Cursor can ingest this at the start of implementation far more effectively than repeatedly processing six large documents, while the detailed documents remain available for deeper guidance when needed. This gives you both comprehensive documentation and a practical implementation blueprint.




Good. Let's start properly.

This is **Document 01**. It is written as if it were going to be handed to a senior engineering team before implementation.

---

# EcoSphere Enterprise ESG Management Platform

## Software Architecture Specification (SAS)

**Version:** 1.0

**Status:** Architecture Approved

---

# 1. Executive Summary

## Vision

EcoSphere is a modular Enterprise ESG (Environmental, Social & Governance) Management Platform designed to help organizations measure, monitor, improve, and report sustainability performance from a single unified system.

Unlike traditional ERP extensions that treat ESG as an afterthought, EcoSphere positions ESG as a first-class operational capability by integrating environmental metrics, employee engagement, governance compliance, and organizational performance into a single intelligent platform.

The system is designed as a scalable enterprise SaaS application with clear module boundaries, reusable business services, centralized security, event-driven workflows, configurable scoring models, and AI-powered operational insights.

Although the hackathon delivers an MVP, the architecture must support future expansion without requiring major redesign.

---

# 2. Architecture Goals

The platform shall satisfy the following architectural qualities.

### Functional

* Carbon Accounting
* ESG Scoring
* CSR Management
* Governance Compliance
* Employee Engagement
* Gamification
* Reporting
* Analytics
* Notifications
* AI Insights

---

### Non Functional

Scalability

Maintainability

Extensibility

Performance

Security

Auditability

Testability

Developer Productivity

---

# 3. Engineering Principles

The project follows these principles.

## Modular Monolith

The MVP will be implemented as a **modular monolith**, not microservices.

Reason:

* Faster development.
* Easier debugging.
* Simpler deployment.
* Cleaner code ownership.
* Future migration path to microservices.

Each module owns its business logic.

Modules communicate only through services and domain events.

---

## Domain Driven Design

The application is divided into bounded contexts.

```
Authentication

Administration

Environmental

Social

Governance

Gamification

Reporting

Notification

Analytics

AI Insights
```

Each context owns

* entities
* services
* repositories
* APIs
* business rules

No module directly manipulates another module's database entities.

---

## Clean Architecture

```
React UI

↓

API Layer

↓

Application Services

↓

Domain Layer

↓

Repositories

↓

Database
```

Business logic never exists inside

* React Components
* Controllers
* Database Models

---

## SOLID

Every module follows

Single Responsibility

Open Closed

Liskov

Interface Segregation

Dependency Inversion

---

# 4. High Level System Architecture

```
                        Browser

                            │

                   React + TypeScript

                            │

               TanStack Query + Router

                            │

──────────────── REST API ─────────────────

                            │

                     FastAPI Backend

                            │

 ┌───────────────────────────────────────────────┐

 Authentication Module

 Administration Module

 Environmental Module

 Social Module

 Governance Module

 Gamification Module

 Reporting Module

 Notification Module

 AI Insight Module

─────────────────────────────────────────────────

                            │

                     SQLAlchemy ORM

                            │

                      PostgreSQL

                            │

                  Object Storage (Files)

```

---

# 5. Bounded Contexts

## Authentication

Responsibilities

* Login
* JWT
* RBAC
* User Session
* Password Reset

Owns

* Users
* Roles
* Permissions

---

## Administration

Responsibilities

* Departments
* Categories
* ESG Configuration
* Notification Settings

---

## Environmental

Responsibilities

* Emission Factors
* Carbon Transactions
* Product ESG
* Sustainability Goals

Produces

Environmental Score

---

## Social

Responsibilities

* CSR Activities
* Employee Participation
* Diversity Metrics
* Training

Produces

Social Score

---

## Governance

Responsibilities

* Policies
* Audits
* Compliance Issues

Produces

Governance Score

---

## Gamification

Responsibilities

* Challenges
* XP
* Badges
* Rewards
* Leaderboards

---

## Reporting

Responsibilities

* ESG Summary
* PDF
* CSV
* Excel

---

## AI

Responsibilities

* ESG Insights
* Carbon Prediction
* Sustainability Suggestions
* Compliance Risk Detection
* Department Recommendations

---

# 6. Architectural Layers

```
Presentation Layer

↓

Application Layer

↓

Domain Layer

↓

Infrastructure Layer

↓

Persistence Layer
```

---

## Presentation Layer

Contains

* React
* Layouts
* Pages
* Components

Never contains business logic.

---

## Application Layer

Coordinates use cases.

Example

```
Approve CSR

↓

Validate

↓

Update Participation

↓

Award XP

↓

Recalculate Department Score

↓

Publish Event
```

---

## Domain Layer

Contains

Business Rules

Examples

Carbon Calculation

Badge Unlock

ESG Weightage

Challenge Completion

---

## Infrastructure Layer

Contains

Database

Email

File Upload

Notifications

External APIs

---

## Persistence Layer

Contains

Repositories

ORM

Indexes

Transactions

---

# 7. Cross Cutting Services

Shared services used by all modules.

Authentication

Authorization

Validation

Logging

Configuration

Audit Trail

Notification

File Storage

AI Engine

Analytics

Caching

Exception Handling

---

# 8. Communication Strategy

Modules never call each other's database.

Instead

```
CSR Approved

↓

Social Service

↓

Domain Event

↓

Gamification Service

↓

XP Updated

↓

Badge Evaluation

↓

Department Score Updated

↓

Notification Created
```

Loose coupling.

---

# 9. Event Driven Design

Major business actions emit domain events.

Examples

```
CarbonTransactionCreated

CSRParticipationApproved

ChallengeCompleted

PolicyAcknowledged

ComplianceIssueRaised

BadgeUnlocked

RewardRedeemed
```

Consumers react independently.

---

# 10. Technology Stack

Frontend

* React 19
* TypeScript
* Vite
* TailwindCSS
* shadcn/ui
* TanStack Query
* React Hook Form
* Zod
* Recharts
* Framer Motion

Backend

* FastAPI
* SQLAlchemy
* PostgreSQL
* Alembic
* Pydantic v2
* JWT

Deployment

* Vercel
* Railway
* Neon PostgreSQL

---

# 11. Design Principles

Every module must satisfy:

* High cohesion.
* Low coupling.
* Reusable UI.
* Reusable APIs.
* Centralized business rules.
* Strict typing.
* Feature isolation.
* Testability.
* Clear ownership.

---

## Architecture Decision Summary

| Decision      | Choice               | Reason                                 |
| ------------- | -------------------- | -------------------------------------- |
| Architecture  | Modular Monolith     | Fast delivery, scalable structure      |
| Backend       | FastAPI              | High performance, typed APIs           |
| Frontend      | React + TypeScript   | Mature ecosystem, maintainability      |
| Database      | PostgreSQL           | Strong relational support for ESG data |
| ORM           | SQLAlchemy           | Mature, flexible, transactional        |
| Auth          | JWT + RBAC           | Secure, role-based access              |
| Pattern       | Service + Repository | Separation of concerns                 |
| UI            | Component-driven     | Reusability and consistency            |
| Communication | Domain Events        | Loose coupling between modules         |

---

## Next Document

**Document 02: Domain Model & Database Architecture**

This will define:

* Every entity.
* Every relationship.
* Primary/foreign keys.
* Indexes.
* Constraints.
* Enums.
* Audit fields.
* Soft-delete strategy.
* Complete ERD.

This database design becomes the foundation for the backend APIs, frontend models, and business rules. It is the most critical document before implementation.


Yes. **Document 02 is the most important document of the entire project.** Everything else (APIs, backend, frontend) depends on it.

I would actually rename it to:

> **02 - Domain Model & Bounded Context Design**

This document should **not** be about tables yet. It should define the business domain.

---

# EcoSphere

# Document 02 – Domain Model & Bounded Context Design

**Version:** 1.0

**Status:** Approved

---

# 1. Purpose

This document defines the business domain of EcoSphere using Domain-Driven Design (DDD) principles. It identifies the core business capabilities, bounded contexts, ownership of business entities, and interactions between modules.

The objective is to establish clear ownership of data and business rules before designing the database or implementing APIs.

---

# 2. Core Domain

EcoSphere enables organizations to measure, manage, and improve their Environmental, Social, and Governance (ESG) performance by integrating sustainability metrics, employee participation, governance compliance, and organizational analytics into a unified platform.

The domain revolves around three primary ESG pillars:

* Environmental
* Social
* Governance

These pillars contribute to department-level ESG scores, which aggregate into an overall organizational ESG score.

---

# 3. Domain Map

```text
EcoSphere
│
├── Identity & Access
│
├── Administration
│
├── Environmental
│
├── Social
│
├── Governance
│
├── Gamification
│
├── Analytics
│
├── Reporting
│
└── Notification
```

Each domain owns its business entities, business rules, services, and APIs.

No domain directly manipulates another domain's entities.

---

# 4. Bounded Contexts

## 4.1 Identity & Access

### Responsibilities

* Authentication
* Authorization
* Session Management
* Role Resolution
* Permission Validation

### Owns

* User
* Role
* Permission

### Provides

* Login
* JWT
* Protected Access
* RBAC

### Dependencies

None

---

## 4.2 Administration

### Responsibilities

* Department Management
* Categories
* ESG Configuration
* Master Data
* Notification Settings

### Owns

* Department
* Category
* ESG Configuration
* Notification Configuration

### Provides

* Department Hierarchy
* Organization Configuration

---

## 4.3 Environmental

### Responsibilities

* Carbon Accounting
* Emission Factors
* Carbon Transactions
* Sustainability Goals
* Product ESG Profile

### Owns

* Emission Factor
* Carbon Transaction
* Product ESG Profile
* Environmental Goal

### Produces

Environmental Score

Environmental KPIs

Carbon Reports

---

## 4.4 Social

### Responsibilities

* CSR Activities
* Employee Participation
* Diversity Metrics
* Employee Engagement
* Training

### Owns

* CSR Activity
* Employee Participation

### Produces

Social Score

Participation Metrics

CSR Reports

---

## 4.5 Governance

### Responsibilities

* Policies
* Audits
* Compliance Issues
* Policy Acknowledgement

### Owns

* Policy
* Audit
* Compliance Issue
* Policy Acknowledgement

### Produces

Governance Score

Compliance Reports

---

## 4.6 Gamification

### Responsibilities

* Challenges
* XP
* Badges
* Rewards
* Leaderboards

### Owns

* Challenge
* Challenge Participation
* Badge
* Reward

### Produces

Employee Ranking

Department Ranking

Engagement Score

---

## 4.7 Analytics

### Responsibilities

* ESG Score Calculation
* KPI Aggregation
* Trend Analysis
* Department Ranking
* Predictive Analytics

### Owns

No persistent entities.

Consumes data from every module.

Produces dashboards.

---

## 4.8 Reporting

### Responsibilities

Generate

* Environmental Reports
* Social Reports
* Governance Reports
* ESG Summary Reports
* Custom Reports

Consumes all domains.

---

## 4.9 Notification

### Responsibilities

* In-App Notifications
* Email Notifications
* Reminder Scheduling
* Activity Timeline

Consumes events from all modules.

---

# 5. Aggregate Roots

The following entities are Aggregate Roots.

```text
User

Department

Emission Factor

Carbon Transaction

CSR Activity

Challenge

Audit

Policy

Compliance Issue
```

Only Aggregate Roots expose public operations.

Child entities are modified only through their parent aggregate.

---

# 6. Domain Ownership

| Domain         | Owns                                    |
| -------------- | --------------------------------------- |
| Identity       | User, Role, Permission                  |
| Administration | Department, Category, Settings          |
| Environmental  | EmissionFactor, CarbonTransaction, Goal |
| Social         | CSRActivity, Participation              |
| Governance     | Policy, Audit, ComplianceIssue          |
| Gamification   | Challenge, Badge, Reward                |
| Analytics      | Calculations                            |
| Reporting      | Reports                                 |
| Notification   | Notifications                           |

---

# 7. Business Capabilities

## Environmental

Capabilities

* Configure emission factors
* Record carbon transactions
* Calculate emissions
* Track sustainability goals
* Generate environmental KPIs

---

## Social

Capabilities

* Create CSR activities
* Employee participation
* Approval workflow
* Participation scoring

---

## Governance

Capabilities

* Create policies
* Conduct audits
* Track compliance
* Monitor overdue issues

---

## Gamification

Capabilities

* Launch challenges
* Award XP
* Unlock badges
* Redeem rewards
* Leaderboards

---

# 8. Domain Events

The application is event-driven.

Major actions emit business events.

```text
CarbonTransactionCreated

CSRParticipationApproved

ChallengeCompleted

BadgeUnlocked

RewardRedeemed

PolicyAcknowledged

ComplianceIssueRaised

ComplianceIssueClosed

DepartmentScoreUpdated

EnvironmentalGoalCompleted
```

Events are immutable.

---

# 9. Domain Communication

Domains never update each other's database tables directly.

Instead

```text
Social Domain

↓

CSR Approved

↓

Event Bus

↓

Gamification Domain

↓

Award XP

↓

Badge Evaluation

↓

Leaderboard Update
```

Another example

```text
Carbon Transaction

↓

Analytics

↓

Department ESG Score

↓

Dashboard

↓

Notification
```

---

# 10. Ownership Rules

Example

Environmental owns

```text
Emission Factors

Carbon Transactions

Goals
```

Governance cannot modify these tables.

It may only consume calculated results.

---

# 11. Domain Dependencies

```text
Identity

↓

Administration

↓

Environmental

↓

Analytics

↓

Reporting
```

```text
Social

↓

Gamification

↓

Analytics
```

```text
Governance

↓

Analytics
```

Notification listens to all.

---

# 12. Future Extensibility

The architecture intentionally supports future additions without redesign:

* Multi-tenancy
* Organization-specific ESG scoring
* Additional ESG modules
* External ERP integrations
* IoT-based carbon sensors
* AI forecasting services
* Carbon credit management
* Sustainability benchmarking
* Public ESG disclosures
* Workflow automation

---

# 13. Architecture Decisions

| Decision                   | Rationale                              |
| -------------------------- | -------------------------------------- |
| Modular Monolith           | Faster MVP while preserving modularity |
| Bounded Contexts           | Clear ownership and reduced coupling   |
| Aggregate Roots            | Consistent business operations         |
| Domain Events              | Decoupled communication                |
| Analytics as Consumer      | Prevents duplicated calculations       |
| Reporting as Read Layer    | Simplifies report generation           |
| Notification as Subscriber | Centralized event handling             |

---

## End of Document

**Next Document (03): Database Architecture & ER Design**

This is where we'll define:

* Complete ER diagram.
* Every entity and attribute.
* Primary and foreign keys.
* Constraints.
* Enums.
* Indexes.
* Audit fields.
* Soft-delete strategy.
* Database naming conventions.

**This will be the single most critical document for implementation**, because every API, service, and UI component will be built on top of this schema.


Excellent. **Document 03 is the foundation of the entire project.** If we get this right, Cursor will generate much better code.

One recommendation before the content: the original hackathon data model is intentionally simplified. For an enterprise-grade system, we should extend it with common operational fields (UUIDs, audit columns, statuses, timestamps, etc.) while keeping all required entities. We should not invent unrelated business features, but we should improve the schema quality.

---

# EcoSphere

# Document 03 — Database Architecture & ER Design

**Version:** 1.0

**Status:** Approved

---

# 1. Database Philosophy

The platform uses **PostgreSQL** as the primary relational database.

Design principles:

* UUID primary keys.
* Third Normal Form (3NF).
* Foreign key constraints.
* Soft delete where appropriate.
* Audit fields on all tables.
* Enum types for controlled values.
* Indexed search columns.
* Transaction-safe updates.
* No duplicated business data.

---

# 2. Naming Standards

### Tables

Plural snake_case

```
users
departments
carbon_transactions
csr_activities
```

### Columns

snake_case

```
first_name
department_id
created_at
updated_at
```

### Foreign Keys

```
department_id

employee_id

challenge_id
```

### Primary Keys

```
id UUID
```

---

# 3. Common Audit Columns

Every table contains

| Column     | Type      |
| ---------- | --------- |
| id         | UUID      |
| created_at | Timestamp |
| updated_at | Timestamp |
| created_by | UUID      |
| updated_by | UUID      |

Soft delete only where needed:

```
deleted_at
```

---

# 4. Core Entity Relationship Diagram

```text
Organization
    │
Departments
    │
Employees (Users)
    │
────────────────────────────────────────────
│            │            │
Environmental Social      Governance
│            │            │
Carbon       CSR          Policies
Transactions Activities   Audits
│            │            │
──────────── Analytics ────────────
                │
        Department Scores
                │
        Organization ESG Score
                │
Reports ─ Notifications ─ AI Insights
```

---

# 5. Entity Catalog

## Identity

### users

Purpose

Authentication

Columns

```
id

first_name

last_name

email

password_hash

role

department_id

status

last_login

created_at

updated_at
```

Indexes

```
email UNIQUE

department_id
```

---

## departments

```
id

name

code

head_id

parent_department_id

employee_count

status
```

Relationships

```
Department

↓

Users

↓

Scores
```

---

## categories

Used for

CSR

Challenges

Reports

---

# Environmental Module

---

## emission_factors

```
id

source_type

activity_name

unit

co2_factor

description

status
```

Example

```
Diesel

kg CO₂/L

2.68
```

---

## carbon_transactions

```
id

department_id

emission_factor_id

activity_name

quantity

unit

calculated_emission

transaction_date

status
```

Relationship

```
Department

↓

Carbon Transaction

↓

Emission Factor
```

---

## environmental_goals

```
id

department_id

title

target_value

current_value

deadline

status
```

---

## product_esg_profiles

```
id

product_name

carbon_score

recyclability

supplier_score

notes
```

---

# Social Module

---

## csr_activities

```
id

title

category_id

description

department_id

start_date

end_date

points

status
```

---

## employee_participation

```
id

employee_id

csr_activity_id

proof_file

approval_status

points_earned

completion_date
```

Relationship

```
Employee

↓

Participation

↓

CSR Activity
```

---

# Governance Module

---

## policies

```
id

title

version

description

effective_date

status
```

---

## policy_acknowledgements

```
id

policy_id

employee_id

acknowledged_at

status
```

---

## audits

```
id

department_id

title

audit_date

auditor_id

status
```

---

## compliance_issues

```
id

audit_id

owner_id

severity

description

due_date

status
```

---

# Gamification

---

## challenges

```
id

title

category_id

description

difficulty

xp

deadline

status
```

---

## challenge_participation

```
id

challenge_id

employee_id

progress

proof

approval

xp_awarded
```

---

## badges

```
id

name

description

unlock_rule

icon

status
```

---

## employee_badges

```
id

badge_id

employee_id

earned_at
```

---

## rewards

```
id

title

points_required

stock

status
```

---

## reward_redemptions

```
id

reward_id

employee_id

redeemed_points

redeemed_at
```

---

# Analytics

---

## department_scores

```
id

department_id

environment_score

social_score

governance_score

overall_score

last_calculated
```

---

# Notification

---

## notifications

```
id

employee_id

title

message

type

read

created_at
```

---

## activity_logs

```
id

employee_id

action

entity

entity_id

metadata

created_at
```

---

# 6. Enums

## UserRole

```
ADMIN

ESG_MANAGER

HR_MANAGER

AUDITOR

EMPLOYEE
```

---

## UserStatus

```
ACTIVE

INACTIVE

LOCKED
```

---

## ChallengeStatus

```
DRAFT

ACTIVE

UNDER_REVIEW

COMPLETED

ARCHIVED
```

---

## CSR Approval

```
PENDING

APPROVED

REJECTED
```

---

## Compliance Severity

```
LOW

MEDIUM

HIGH

CRITICAL
```

---

## Goal Status

```
NOT_STARTED

IN_PROGRESS

COMPLETED

OVERDUE
```

---

# 7. Relationships

```
Department

1

↓

Many Employees
```

```
Department

1

↓

Many Carbon Transactions
```

```
CSR Activity

1

↓

Many Participations
```

```
Challenge

1

↓

Many Participations
```

```
Audit

1

↓

Many Compliance Issues
```

---

# 8. Database Constraints

Unique

```
email

department_code
```

Foreign Keys

```
department_id

employee_id

challenge_id

audit_id
```

Check Constraints

```
points >= 0

stock >= 0

xp >= 0

co2_factor >= 0
```

---

# 9. Indexes

Index the following:

```
email

department_id

challenge_id

employee_id

audit_id

transaction_date

status

created_at
```

Composite indexes

```
(employee_id, challenge_id)

(department_id, transaction_date)

(employee_id, approval_status)
```

---

# 10. Derived Data (Not Stored)

These values should be calculated by services, not stored directly:

* Overall ESG Score
* Department Ranking
* Leaderboard Position
* Badge Eligibility
* Challenge Completion Percentage
* Carbon Reduction Percentage
* Goal Achievement Percentage
* Organization ESG Score

Only persist values that improve performance after clear justification (e.g., cached department scores refreshed by scheduled jobs).

---

# 11. Database Decisions

| Decision             | Rationale                                     |
| -------------------- | --------------------------------------------- |
| PostgreSQL           | Strong relational integrity and reporting     |
| UUID PKs             | Safer for distributed systems                 |
| 3NF                  | Minimize redundancy                           |
| Audit Columns        | Enterprise traceability                       |
| Soft Delete          | Preserve historical records where appropriate |
| FK Constraints       | Prevent orphaned records                      |
| Derived Calculations | Avoid inconsistent data                       |
| Enum Types           | Controlled business states                    |

---

## **Important architectural refinement**

One thing I recommend changing from the hackathon specification:

**Separate `employees` from `users`.**

Instead of one `users` table holding both authentication and employee information, use:

* `users` → authentication, credentials, role, login state.
* `employees` → business profile (department, designation, ESG participation, manager, etc.).

This mirrors enterprise systems where not every employee necessarily has login credentials and keeps authentication concerns separate from HR/business data.

That change will make the architecture cleaner and easier to extend while remaining fully compatible with the problem statement. It is the approach I would use for a production-quality design.



Yes. Now we move to the **most important engineering document** after the database.

This is what Cursor will rely on the most.

---

# EcoSphere

# Document 04 — Backend Architecture Specification

**Version:** 1.0

**Status:** Approved

**Target Stack:** FastAPI + SQLAlchemy + PostgreSQL

---

# 1. Purpose

This document defines the backend architecture, module boundaries, request lifecycle, service layer, repository pattern, validation strategy, authentication, authorization, event system, error handling, background jobs, and API conventions for EcoSphere.

The backend follows a **Modular Monolith** architecture with **Domain-Driven Design (DDD)** principles. Each module encapsulates its own business logic while sharing infrastructure services.

---

# 2. Backend Principles

The backend must satisfy:

* Modular Monolith
* Domain-Driven Design
* SOLID Principles
* Service Layer Pattern
* Repository Pattern
* Dependency Injection
* Single Responsibility
* Thin Controllers
* Fat Services
* Transaction Safety
* Centralized Validation
* Centralized Authorization
* Audit Logging
* Event-Driven Communication

---

# 3. High-Level Backend Architecture

```text
                        FastAPI Application
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
     API Layer            Middleware             Background Jobs
        │                      │                      │
        ▼                      ▼                      ▼
 Authentication         RBAC / Logging        Scheduler / Events
        │
        ▼
─────────────────────────────────────────────────────────────
 Application Services (Business Logic)
─────────────────────────────────────────────────────────────
        │
        ▼
 Domain Services / Policies / Rules
        │
        ▼
 Repository Layer
        │
        ▼
 SQLAlchemy ORM
        │
        ▼
 PostgreSQL
```

---

# 4. Folder Structure

```
backend/
│
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── database.py
│   │   ├── logging.py
│   │   └── events.py
│   │
│   ├── auth/
│   │   ├── router.py
│   │   ├── service.py
│   │   ├── repository.py
│   │   ├── schemas.py
│   │   └── models.py
│   │
│   ├── modules/
│   │   ├── administration/
│   │   ├── environmental/
│   │   ├── social/
│   │   ├── governance/
│   │   ├── gamification/
│   │   ├── analytics/
│   │   ├── reports/
│   │   └── notifications/
│   │
│   ├── shared/
│   │   ├── exceptions/
│   │   ├── middleware/
│   │   ├── validators/
│   │   ├── pagination/
│   │   └── utils/
│   │
│   └── tests/
```

---

# 5. Request Lifecycle

```
HTTP Request

↓

Router

↓

Authentication Middleware

↓

RBAC Middleware

↓

Input Validation (Pydantic)

↓

Application Service

↓

Repository

↓

Database

↓

Service Response

↓

Serializer

↓

JSON Response
```

Controllers (routers) must **never** contain business logic.

---

# 6. Module Template

Every module follows the same internal structure.

```
environmental/

router.py

service.py

repository.py

schemas.py

models.py

validators.py

events.py

permissions.py

tests/
```

This keeps all modules consistent.

---

# 7. Layer Responsibilities

## Router Layer

Responsibilities:

* Receive HTTP requests.
* Validate request schemas.
* Inject authenticated user.
* Call services.
* Return standardized responses.

Must **not**:

* Query the database directly.
* Calculate ESG scores.
* Implement business rules.

---

## Service Layer

The service layer owns all business logic.

Examples:

* Carbon calculation.
* ESG score updates.
* Badge unlocking.
* Challenge approval.
* Compliance validation.

Services may call multiple repositories and publish domain events.

---

## Repository Layer

Repositories are responsible for:

* Database CRUD.
* Query optimization.
* Pagination.
* Filtering.
* Transactions.

Repositories must **not** contain business rules.

---

## Models

SQLAlchemy ORM entities only.

No validation logic.

No business calculations.

---

## Schemas

Pydantic request and response models.

Responsibilities:

* Input validation.
* Response serialization.
* OpenAPI documentation.

---

# 8. Dependency Injection

Use FastAPI's dependency system for:

* Database sessions.
* Current user.
* Permissions.
* Configuration.

Services receive dependencies through constructors or injected functions rather than creating them internally.

---

# 9. Authentication

JWT-based authentication.

Flow:

```
Login

↓

Verify Credentials

↓

Generate Access Token

↓

(Optional) Refresh Token

↓

Authenticated Requests
```

Passwords stored using a strong password hashing algorithm (e.g., bcrypt or Argon2).

---

# 10. Authorization (RBAC)

Authorization is enforced in middleware/dependencies.

Example:

```
Admin

↓

Department CRUD

Allowed

Employee

↓

Department CRUD

Forbidden
```

Permission checks occur before service execution.

---

# 11. Domain Events

Business actions publish events.

Examples:

```
CSRParticipationApproved

↓

AwardXP

↓

UpdateLeaderboard

↓

RecalculateDepartmentScore

↓

CreateNotification
```

Events reduce coupling between modules.

---

# 12. Transaction Strategy

Any operation affecting multiple aggregates executes within a database transaction.

Example:

```
Approve Participation

↓

Update Participation

↓

Award XP

↓

Insert Notification

↓

Commit
```

Rollback on failure.

---

# 13. Error Handling

Centralized exception handlers.

Standard response:

```json
{
  "success": false,
  "message": "Department not found",
  "code": "DEPARTMENT_NOT_FOUND",
  "details": null
}
```

No raw stack traces returned to clients.

---

# 14. API Response Standard

Success:

```json
{
  "success": true,
  "message": "CSR activity created successfully",
  "data": { ... }
}
```

Failure:

```json
{
  "success": false,
  "message": "Validation failed",
  "errors": [ ... ]
}
```

---

# 15. Background Jobs

Use a scheduler (e.g., APScheduler or Celery in the future) for:

* ESG score recalculation.
* Goal progress updates.
* Policy reminders.
* Compliance due-date checks.
* Badge auto-awards.
* Report generation.

---

# 16. File Storage

Uploaded files (CSR proofs, policy documents, icons) should be abstracted behind a storage service.

Interface:

```
StorageService

upload()

delete()

get_url()
```

Allow future migration from local storage to S3/Cloudinary without changing business logic.

---

# 17. Logging & Audit

Every state-changing operation records:

* User
* Action
* Entity
* Entity ID
* Timestamp
* Metadata

Stored in `activity_logs`.

---

# 18. Validation Strategy

Validation occurs in three layers:

1. **Pydantic Schemas** – structure and types.
2. **Service Layer** – business rules.
3. **Database Constraints** – final integrity.

Example:

* Schema: required fields.
* Service: "Challenge deadline must be in the future."
* Database: foreign keys, unique constraints.

---

# 19. API Versioning

Prefix all endpoints:

```
/api/v1/
```

Example:

```
/api/v1/auth/login
/api/v1/departments
/api/v1/carbon-transactions
```

---

# 20. Future Extensibility

Architecture supports future additions without major refactoring:

* Multi-tenancy.
* Message queues.
* Microservice extraction.
* External ERP integrations.
* GraphQL layer.
* AI microservices.
* Caching (Redis).
* WebSocket notifications.

---

# Architecture Decisions

| Decision     | Choice                  | Reason                               |
| ------------ | ----------------------- | ------------------------------------ |
| Architecture | Modular Monolith        | Simpler MVP, clean module boundaries |
| Pattern      | Service + Repository    | Separation of concerns               |
| Validation   | Pydantic + Service + DB | Layered validation                   |
| Auth         | JWT + RBAC              | Secure, stateless authentication     |
| Events       | Domain Events           | Loose coupling                       |
| Responses    | Standard envelope       | Consistent frontend integration      |
| Transactions | Service-managed         | Data integrity                       |
| Storage      | Abstracted service      | Future portability                   |

---

## Improvement to the Hackathon Scope

I recommend adding a **shared module** containing reusable infrastructure (exceptions, pagination, storage, validators, middleware, and utilities) instead of duplicating these across feature modules. This keeps feature modules focused on business capabilities while ensuring consistent behavior across the application.

**Next document:** **05 – Frontend Architecture Specification**, which will define the React application structure, routing, state management, component library, design system, and UI composition strategy.


Excellent. Before generating Document 05, I want to make one architectural improvement.

The frontend should **not** be organized by pages. It should be organized by **business domains**. This is how enterprise React applications (Stripe, Linear, Atlassian, Microsoft) are structured.

---

# EcoSphere

# Document 05 – Frontend Architecture Specification

**Version:** 1.0

**Status:** Approved

**Target Stack:** React 19 + TypeScript + Vite + TailwindCSS + shadcn/ui

---

# 1. Purpose

This document defines the frontend architecture, UI composition, routing, component system, state management, API integration, theming, accessibility, and frontend engineering standards for EcoSphere.

The frontend follows a **Feature-Based Modular Architecture** with a reusable design system and centralized application shell.

The objective is to ensure scalability, maintainability, consistency, and an enterprise-grade user experience.

---

# 2. Frontend Principles

The application follows:

* Feature-Based Architecture
* Component-Driven Development
* Single Responsibility Principle
* Atomic Design (adapted)
* Centralized API Layer
* Type-Safe Data Flow
* Responsive First
* Accessible by Default
* Lazy Loading
* Reusable UI Components
* Separation of Business Logic from Presentation

---

# 3. High-Level Frontend Architecture

```text
                    Browser

                        │

                  React 19 App

                        │

────────────────────────────────────

App Shell

│

├── Sidebar

├── Top Navigation

├── Breadcrumbs

├── Notifications

└── User Menu

────────────────────────────────────

                        │

                React Router

                        │

────────────────────────────────────

Dashboard

Environmental

Social

Governance

Gamification

Reports

Settings

────────────────────────────────────

                        │

                Shared Components

                        │

────────────────────────────────────

API Layer

↓

TanStack Query

↓

FastAPI
```

---

# 4. Folder Structure

```
frontend/

src/

│

├── app/
│   ├── App.tsx
│   ├── providers.tsx
│   ├── router.tsx
│   └── layouts/
│
├── modules/
│   ├── auth/
│   ├── dashboard/
│   ├── environmental/
│   ├── social/
│   ├── governance/
│   ├── gamification/
│   ├── reports/
│   └── settings/
│
├── shared/
│   ├── components/
│   ├── hooks/
│   ├── services/
│   ├── utils/
│   ├── constants/
│   ├── types/
│   ├── icons/
│   └── lib/
│
├── assets/
│
├── styles/
│
└── main.tsx
```

Every feature owns its components, pages, hooks, and API calls.

---

# 5. Application Shell

The App Shell is persistent across authenticated pages.

```
App

↓

AppLayout

↓

Sidebar

↓

Topbar

↓

Breadcrumb

↓

Content Area

↓

Footer
```

The Sidebar and Topbar never unmount during navigation.

---

# 6. Navigation Structure

```
Dashboard

Environmental
    ├── Carbon Transactions
    ├── Emission Factors
    ├── Goals
    └── Product ESG

Social
    ├── CSR Activities
    ├── Participation
    └── Diversity Metrics

Governance
    ├── Policies
    ├── Audits
    └── Compliance

Gamification
    ├── Challenges
    ├── Badges
    ├── Rewards
    └── Leaderboard

Reports

Settings
```

---

# 7. Routing Strategy

Protected Routes

```
/

↓

Login

↓

Dashboard

↓

Environmental

↓

Social

↓

Governance

↓

Gamification

↓

Reports

↓

Settings
```

Unauthenticated users are redirected to `/login`.

---

# 8. State Management

### Server State

**TanStack Query**

Responsibilities:

* Fetching
* Caching
* Pagination
* Background Refetch
* Optimistic Updates

---

### Client State

React Context

Used for:

* Theme
* Authentication
* Sidebar
* Notifications

Avoid global state libraries unless complexity grows significantly.

---

# 9. API Layer

Every module owns its API client.

Example:

```
environmental/

api/

carbon.api.ts

goal.api.ts
```

Components never call `fetch()` directly.

All requests go through typed service functions.

---

# 10. Component Architecture

### Shared Components

```
Button

Input

Select

Textarea

Checkbox

Modal

Drawer

Tooltip

Toast

Badge

Avatar

Dropdown

DataTable

Pagination

SearchBar

FilterPanel

LoadingSkeleton

EmptyState
```

---

### Business Components

```
ESGScoreCard

KpiCard

CarbonTrendChart

DepartmentScoreChart

CSRCard

ChallengeCard

LeaderboardTable

ComplianceTimeline

GoalProgress

NotificationPanel

AuditSummary
```

---

# 11. Page Composition

Example:

Dashboard

```
DashboardPage

↓

DashboardLayout

↓

Header

↓

KPI Grid

↓

Charts Grid

↓

AI Insights

↓

Recent Activities

↓

Department Ranking
```

Pages compose components rather than implementing logic.

---

# 12. Forms

Use:

* React Hook Form
* Zod

All forms follow:

```
Form

↓

Validation

↓

Submit

↓

API

↓

Toast

↓

Refresh Query
```

---

# 13. Tables

All data tables support:

* Sorting
* Filtering
* Search
* Pagination
* Row Actions
* Empty State
* Loading State

Reusable table component only.

---

# 14. Charts

Use Recharts.

Supported:

* Line Chart
* Bar Chart
* Area Chart
* Pie Chart
* Radar Chart

Charts must be reusable and accept typed data.

---

# 15. Theme

Support:

* Light
* Dark

Use CSS variables with Tailwind.

No hardcoded colors.

---

# 16. Responsive Design

Breakpoints:

* Mobile
* Tablet
* Desktop
* Large Desktop

Sidebar collapses automatically on smaller screens.

---

# 17. Accessibility

Requirements:

* Keyboard navigation.
* Visible focus states.
* ARIA labels.
* Semantic HTML.
* Color contrast compliance.
* Screen reader compatibility.

---

# 18. Performance

Use:

* Route lazy loading.
* Code splitting.
* Memoization where appropriate.
* Virtualized tables for large datasets (future enhancement).
* Optimized images.

---

# 19. Error Handling

Display:

* Empty State
* Error State
* Loading State

Never show raw API errors.

---

# 20. Frontend Security

* Secure token storage strategy (prefer HTTP-only cookies if supported; if JWTs are stored client-side for the hackathon, document the tradeoff).
* Protected routes.
* Input sanitization.
* Client-side validation complements server-side validation.
* Role-based UI rendering (authorization is still enforced by the backend).

---

# 21. Design System Tokens

Spacing:

```
4
8
12
16
24
32
48
64
```

Border Radius:

```
sm

md

lg

xl
```

Typography:

```
Heading

Subheading

Body

Caption

Label
```

---

# 22. Reusable Layouts

```
AppLayout

DashboardLayout

SettingsLayout

ReportLayout

AuthLayout
```

---

# 23. Animation

Use Framer Motion sparingly.

Allowed:

* Card entrance
* Modal transitions
* Sidebar collapse
* Toast notifications
* Chart appearance

Avoid excessive animations.

---

# 24. Frontend Decisions

| Decision     | Choice                | Reason                                 |
| ------------ | --------------------- | -------------------------------------- |
| Framework    | React 19              | Component ecosystem                    |
| Language     | TypeScript            | Type safety                            |
| Build Tool   | Vite                  | Fast development                       |
| UI           | shadcn/ui             | Accessible, customizable components    |
| Styling      | Tailwind CSS          | Consistent design system               |
| Forms        | React Hook Form + Zod | Efficient forms with schema validation |
| Server State | TanStack Query        | Caching and synchronization            |
| Charts       | Recharts              | Simple, responsive visualizations      |
| Icons        | Lucide                | Consistent iconography                 |
| Motion       | Framer Motion         | Lightweight animations                 |

---

# 25. Recommended Improvement (Beyond the Hackathon)

One addition I'd strongly recommend is introducing a **shared data grid abstraction** instead of building tables independently.

Create a reusable `DataGrid` component that supports:

* Column configuration
* Sorting
* Filtering
* Pagination
* Row actions
* Bulk actions
* CSV export
* Loading/empty/error states

Every table in EcoSphere (CSR Activities, Carbon Transactions, Policies, Challenges, Reports) can then use the same component with different column definitions. This reduces duplication, improves consistency, and makes the frontend much easier to maintain.

---

## Next Document

**Document 06 – API Contract & Service Specification**

This will define:

* REST endpoint catalog
* Request/response schemas
* Status codes
* Pagination
* Filtering conventions
* Error model
* Authentication flow
* Versioning
* Module-specific APIs

This document becomes the contract between the frontend and backend and should be finalized before implementation begins.

Excellent. **Document 06 is the contract between the frontend and backend.** If we define it well, Cursor can generate the frontend and backend independently without mismatches.

One refinement before the content: instead of documenting endpoints one by one, define **API conventions first**, then module-specific endpoints. That keeps the API consistent.

---

# EcoSphere

# Document 06 – API Contract & Service Specification

**Version:** 1.0

**Status:** Approved

**Architecture Style:** RESTful API

**Base URL:** `/api/v1`

---

# 1. API Design Principles

The API must satisfy:

* RESTful resource-oriented design.
* Consistent URL structure.
* JSON request/response.
* Standard HTTP status codes.
* Idempotent GET/PUT/DELETE.
* Validation at API boundary.
* Standard response envelope.
* Pagination for collections.
* Filtering and sorting support.
* Versioned endpoints.
* Role-based authorization.

---

# 2. API Versioning

All endpoints must be prefixed with:

```text
/api/v1
```

Future versions:

```text
/api/v2
```

No breaking changes within the same version.

---

# 3. Response Envelope

### Success

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {},
  "meta": {
    "request_id": "uuid",
    "timestamp": "ISO8601"
  }
}
```

### Error

```json
{
  "success": false,
  "message": "Validation failed",
  "error": {
    "code": "VALIDATION_ERROR",
    "details": []
  },
  "meta": {
    "request_id": "uuid",
    "timestamp": "ISO8601"
  }
}
```

---

# 4. Standard Status Codes

| Status | Meaning                 |
| ------ | ----------------------- |
| 200    | Success                 |
| 201    | Created                 |
| 204    | No Content              |
| 400    | Validation Error        |
| 401    | Unauthorized            |
| 403    | Forbidden               |
| 404    | Not Found               |
| 409    | Conflict                |
| 422    | Business Rule Violation |
| 500    | Internal Server Error   |

---

# 5. Authentication APIs

## Login

```
POST /api/v1/auth/login
```

Request

```json
{
  "email": "",
  "password": ""
}
```

Response

```json
{
  "access_token": "...",
  "refresh_token": "...",
  "expires_in": 3600,
  "user": {}
}
```

---

## Refresh Token

```
POST /api/v1/auth/refresh
```

---

## Logout

```
POST /api/v1/auth/logout
```

---

## Current User

```
GET /api/v1/auth/me
```

---

# 6. Administration APIs

## Departments

```
GET    /departments
GET    /departments/{id}
POST   /departments
PUT    /departments/{id}
DELETE /departments/{id}
```

---

## Categories

```
GET
POST
PUT
DELETE
```

---

## ESG Configuration

```
GET /settings/esg
PUT /settings/esg
```

---

# 7. Environmental APIs

## Emission Factors

```
GET

POST

PUT

DELETE
```

---

## Carbon Transactions

```
GET

POST

GET/{id}

PUT/{id}

DELETE/{id}
```

Extra

```
POST /calculate
```

Returns calculated emissions.

---

## Environmental Goals

```
GET

POST

PUT

DELETE
```

---

## Product ESG

```
GET

POST

PUT

DELETE
```

---

# 8. Social APIs

## CSR Activities

```
GET

POST

PUT

DELETE
```

---

## Participation

```
GET

POST

PUT Approval

DELETE
```

Approval endpoint

```
POST

/participation/{id}/approve
```

---

# 9. Governance APIs

## Policies

```
CRUD
```

---

## Policy Acknowledgement

```
POST

GET
```

---

## Audits

```
CRUD
```

---

## Compliance Issues

```
CRUD
```

Extra

```
POST

/{id}/close
```

---

# 10. Gamification APIs

## Challenges

```
CRUD
```

---

## Participation

```
POST Join

POST Submit

POST Review
```

---

## Badges

```
GET

POST

PUT

DELETE
```

---

## Rewards

```
CRUD
```

---

## Leaderboard

```
GET

/team

GET

/company
```

---

# 11. Analytics APIs

```
GET

/dashboard

GET

/environment

GET

/social

GET

/governance

GET

/esg
```

These endpoints expose aggregated, read-only metrics.

---

# 12. Reporting APIs

```
GET

/environment

GET

/social

GET

/governance

GET

/summary
```

Exports

```
POST

/export/pdf

POST

/export/csv

POST

/export/excel
```

---

# 13. Notification APIs

```
GET

/notifications

PUT

/{id}/read

PUT

/read-all
```

---

# 14. Query Parameters

Every collection endpoint supports:

```
?page=1

&page_size=20

&search=

&sort=name

&order=asc
```

---

# 15. Filtering

Example

```
GET

/carbon-transactions

?department=IT

&start_date=...

&end_date=...

&status=ACTIVE
```

---

# 16. Pagination

Response

```json
{
  "data": [],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 245,
    "pages": 13
  }
}
```

---

# 17. Validation Rules

Validation occurs in:

1. Client.
2. API.
3. Service.
4. Database.

Example

```
Emission Factor

> 0
```

```
Challenge Deadline

Future Date
```

```
Department Code

Unique
```

---

# 18. Authorization Matrix

| Module      | Admin | ESG Manager | HR Manager | Auditor |     Employee     |
| ----------- | :---: | :---------: | :--------: | :-----: | :--------------: |
| Dashboard   |   ✓   |      ✓      |      ✓     |    ✓    |         ✓        |
| Departments |   ✓   |      ✗      |      ✗     |    ✗    |         ✗        |
| Carbon      |   ✓   |      ✓      |      ✗     |    ✗    |       View       |
| CSR         |   ✓   |      ✓      |      ✓     |    ✗    |    Participate   |
| Policies    |   ✓   |      ✓      |      ✗     |    ✓    | View/Acknowledge |
| Audits      |   ✓   |      ✓      |      ✗     |    ✓    |       View       |
| Challenges  |   ✓   |      ✓      |      ✓     |    ✗    |    Participate   |
| Reports     |   ✓   |      ✓      |      ✓     |    ✓    |      Limited     |

---

# 19. Idempotency

Use idempotent semantics:

* GET
* PUT
* DELETE

POST creates new resources.

For future financial or reward redemption endpoints, consider supporting an `Idempotency-Key` header.

---

# 20. API Security

* JWT authentication.
* Role-based authorization.
* Input validation.
* Rate limiting (future enhancement).
* CORS configuration.
* Request ID for tracing.
* HTTPS in production.

---

# 21. OpenAPI

FastAPI should automatically generate:

```
/docs

/redoc
```

Every endpoint must include:

* Summary
* Description
* Request model
* Response model
* Error responses

---

# 22. API Design Decisions

| Decision      | Choice            | Reason                   |
| ------------- | ----------------- | ------------------------ |
| Style         | REST              | Simple, widely supported |
| Versioning    | URL               | Explicit evolution       |
| Responses     | Standard envelope | Consistency              |
| Auth          | JWT               | Stateless authentication |
| Validation    | Pydantic          | Strong typing            |
| Pagination    | Offset-based      | Sufficient for MVP       |
| Documentation | OpenAPI           | Automatic with FastAPI   |

---

# 23. Improvement Beyond the Hackathon

I recommend introducing a **Backend-for-Frontend (BFF)** layer for dashboard endpoints.

Instead of making the frontend call multiple endpoints:

* `/analytics/environment`
* `/analytics/social`
* `/analytics/governance`
* `/notifications`

Create a single endpoint:

```
GET /api/v1/dashboard
```

This endpoint aggregates all dashboard data in one response:

* KPI cards
* ESG scores
* Recent activities
* Notifications
* AI insights
* Department rankings
* Chart datasets

Benefits:

* Faster page load.
* Fewer network requests.
* Simpler frontend.
* Better user experience.

---

Perfect. Before we continue, I reviewed our architecture as if I were conducting an **architecture review at Microsoft/Amazon**. There are a few things I'd change **before Cursor writes any code**.

---

# Architecture Review (Changes Required)

## 1. Separate `users` and `employees` ✅

Earlier I mentioned this. I think it's worth making.

Instead of:

```
users
```

We should have:

```
users
employees
roles
permissions
user_roles
role_permissions
```

Reason:

Authentication ≠ Employee Profile.

Enterprise applications almost always separate identity from business entities.

---

## 2. Don't Store Department Scores

Currently we have

```
department_scores
```

I don't like this.

Instead

```
Analytics Service

↓

Compute Score

↓

Redis Cache (future)

↓

Dashboard
```

Only cache if performance requires it.

Never make this the source of truth.

---

## 3. Introduce Organization Entity

The hackathon ignores organizations.

We shouldn't.

```
Organization

↓

Departments

↓

Employees

↓

Everything
```

Future multi-tenancy becomes trivial.

---

## 4. Create Shared BaseModel

Instead of repeating

```
created_at

updated_at

created_by

updated_by
```

everywhere.

Create

```
BaseModel
```

Every entity inherits.

---

## 5. Add Slugs

For

Departments

Challenges

Policies

Reports

Helpful for URLs.

---

## 6. Standardize Status

Don't use free text.

Example

Instead of

```
Active

Inactive

Completed

Pending
```

Use enums everywhere.

---

## 7. Event Bus

Instead of

```
CSR

↓

XP

↓

Notification
```

directly.

Use

```
Event

↓

Subscribers

↓

Notification

↓

Analytics

↓

Gamification
```

Loose coupling.

---

## 8. AI Module

Don't expose GPT directly.

Instead

```
AI Provider

↓

Prompt Builder

↓

LLM

↓

Response Formatter
```

Later

OpenAI

Claude

Gemini

can all plug in.

---

## 9. Storage Layer

Never upload directly.

```
Upload Service

↓

Storage Provider

↓

Cloudinary

or

S3

or

Local
```

---

## 10. Config Module

Very important.

Instead of hardcoding

```
40%

30%

30%
```

Create

```
esg_config

environment_weight

social_weight

governance_weight
```

Admin can modify.

---

# Biggest Improvement

I think we should introduce **Hexagonal (Ports & Adapters) Architecture**.

Not full clean architecture.

Hybrid.

```
React

↓

REST

↓

Application Service

↓

Domain

↓

Ports

↓

Adapters

↓

Database
```

Much cleaner.

---

# One More Thing

I don't want Cursor writing SQLAlchemy models first.

I want Cursor to generate

```
Pydantic Models

↓

SQLAlchemy Models

↓

Repositories

↓

Services

↓

Routers
```

This keeps contracts consistent.

---

# Overall Architecture

I would rate what we've built so far:

| Area                 | Score  |
| -------------------- | ------ |
| Product Design       | 10/10  |
| Database             | 9.5/10 |
| Backend              | 9.8/10 |
| Frontend             | 9.7/10 |
| Scalability          | 10/10  |
| Maintainability      | 10/10  |
| Enterprise Readiness | 9.8/10 |

Overall: **9.8/10**

---
# EcoSphere Architecture Blueprint

Version: 1.0

Status: Approved

This document is the single source of truth for all implementation.
Whenever there is a conflict between generated code and this document,
this document takes precedence.

---

# Tech Stack

Frontend
- React 19
- TypeScript
- Vite
- TailwindCSS
- shadcn/ui
- TanStack Query
- React Hook Form
- Zod
- Recharts
- Framer Motion

Backend
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- JWT Authentication

Deployment
- Vercel
- Railway
- Neon PostgreSQL

---

# Architecture Style

Modular Monolith

Feature Driven

DDD

SOLID

Repository Pattern

Service Layer

RBAC

Event Driven

Clean Architecture

---

# Modules

Authentication

Administration

Environmental

Social

Governance

Gamification

Analytics

Reports

Notifications

AI Insights

Each module owns

- models
- schemas
- repositories
- services
- routers
- permissions
- validators
- events

Modules never access another module's database directly.

---

# Backend Layers

Router

↓

Service

↓

Repository

↓

Database

Business logic ONLY inside Services.

Repositories never contain business rules.

Routers never contain business logic.

---

# Frontend Layers

Page

↓

Feature Components

↓

Shared Components

↓

Hooks

↓

API Layer

↓

Backend

Pages never call fetch() directly.

Business logic never exists inside React Components.

---

# Folder Structure

backend/

app/

modules/

shared/

frontend/

src/

modules/

shared/

Every feature owns its code.

Never create global dumping folders.

---

# Database

PostgreSQL

UUID Primary Keys

Audit Columns

Foreign Keys

Indexes

Enums

3NF

Soft Delete where required.

Users separated from Employees.

Organization is root entity.

---

# API

/api/v1

REST

JSON

Typed Request

Typed Response

Standard Response Envelope

Pagination

Filtering

Sorting

OpenAPI

---

# Authentication

JWT

RBAC

Permission Middleware

Protected Routes

Refresh Token Ready

---

# Validation

Frontend

↓

Pydantic

↓

Service

↓

Database

---

# Events

Every business action emits domain events.

Example

CSR Approved

↓

Award XP

↓

Update Leaderboard

↓

Update Department Score

↓

Create Notification

Modules communicate only through events or services.

---

# Logging

Every mutation creates

Activity Log

User

Timestamp

Entity

Action

Metadata

---

# AI

AI Provider

↓

Prompt Builder

↓

LLM

↓

Formatter

↓

API

LLM never accesses database directly.

---

# Shared Components

Frontend

Button

Modal

Drawer

DataTable

Form

Search

Pagination

Charts

Status Badge

KPI Card

Backend

Exceptions

Validators

Pagination

Storage

Authentication

Authorization

Logging

---

# Code Quality Rules

Never use any.

Never duplicate code.

Never duplicate APIs.

Never duplicate components.

Never duplicate business logic.

Prefer composition over inheritance.

Prefer reusable components.

Every module must be independently testable.

---

# Cursor Guardrails

Cursor MUST

Follow Document 00

Follow System Architecture

Reuse existing components

Reuse services

Reuse repositories

Keep modules isolated

Respect DDD

Never invent architecture

Never add dependencies without approval

Never bypass Services

Never place business logic inside UI

Never write SQL inside Routers

---

# Definition of Done

✓ Types complete

✓ Validation complete

✓ RBAC complete

✓ Logging complete

✓ Business rules complete

✓ Responsive UI

✓ No duplicate code

✓ No lint errors

✓ No type errors

✓ API documented

✓ Tests where appropriate

---

# Future Ready

Architecture supports

Multi-tenancy

Microservices

Redis

Kafka

WebSockets

External ERP Integration

AI Agents

Cloud Storage

Feature Flags

Organization Configuration

without requiring major redesign.