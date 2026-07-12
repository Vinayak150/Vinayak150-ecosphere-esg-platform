# EcoSphere — Release Notes

**Version:** 1.0.0  
**Release Date:** July 2026  
**Codename:** Foundation & ESG Core  
**Status:** Production-ready modular monolith

---

## Overview

EcoSphere 1.0.0 delivers an enterprise-grade Environmental, Social, and Governance (ESG) management platform. This release implements the full core business surface area defined in `SYSTEM_BLUEPRINT.md`: authentication and RBAC, executive dashboard, Environmental, Social, Governance, and Gamification modules — with matching React dashboards, API coverage, database migrations, automated tests, and demo seed data.

The platform is designed as a **modular monolith**: each feature owns its models, schemas, repository, service, router, permissions, events, and frontend module. Business logic lives exclusively in service layers; authorization is enforced server-side on every protected endpoint.

---

## Features Implemented

### Platform Foundation

| Capability | Description |
|------------|-------------|
| Authentication | JWT access and refresh tokens, login, logout, token rotation, session introspection |
| RBAC | Five roles (Admin, ESG Manager, HR Manager, Auditor, Employee) with 20 granular permissions |
| API envelope | Standardized success/error responses with request metadata on `/api/v1` |
| Activity logging | Immutable audit trail for mutations across all business modules |
| Domain events | Event bus for cross-module notifications (login, CSR, governance, gamification) |
| Health check | `GET /api/v1/health` for service and environment status |
| Migrations | Six Alembic revisions (foundation → environmental → social → governance → gamification → indexes) |
| Demo seed data | 12-month realistic dataset via `python -m scripts.seed_data --reset` |
| CI/CD | GitHub Actions pipeline: lint, typecheck, migrations, tests, and production build |

### Executive Dashboard

- Composite ESG score across Environmental, Social, and Governance pillars
- Department environmental ranking with goal completion metrics
- Recent carbon transactions and activity feed
- Goal progress, monthly carbon trend, and top emission sources
- Contextual notifications and permission-aware quick actions
- Gamification widgets: XP leaderboard, top performers, recent badge unlocks, challenge progress

### Environmental Module

- **Emission factors** — CRUD with source type, unit, and CO₂ conversion factors
- **Carbon transactions** — Department-scoped activity logging with automatic emission calculation
- **Environmental goals** — Department targets with progress tracking and status lifecycle
- **Product ESG profiles** — Carbon, recyclability, and supplier scores per product
- **Analytics dashboard** — Aggregated environmental KPIs, trends, and department breakdowns
- **Carbon calculator endpoint** — Server-side emission computation from factor and quantity

### Social Module

- **CSR activities** — Department-scoped programs with categories, points, evidence requirements, and date ranges
- **Employee participation** — Join, submit, approve/reject workflow with points allocation
- **Analytics dashboard** — Participation rates, monthly CSR trends, top departments
- **Department and employee directory** — Supporting endpoints for form population

### Governance Module

- **Policies** — Versioned policy documents with effective dates and status management
- **Policy acknowledgements** — Employee attestation tracking with timestamps
- **Audits** — Department audits with auditor assignment and status lifecycle
- **Compliance issues** — Severity-based issues with due dates, overdue auto-flagging, and close workflow
- **Analytics dashboard** — Governance score, compliance rate, open/overdue issues, policy completion

### Gamification Module

- **Challenges** — Categorized sustainability challenges with XP, difficulty, deadlines, and evidence requirements
- **Participation workflow** — Join → submit proof → manager review → XP award
- **Badges** — Rule-based unlock system (`total_xp`, `approved_challenges`) with automatic evaluation
- **Rewards** — XP redemption catalog with stock management
- **Leaderboards** — Company-wide and department rankings with badge counts
- **Analytics dashboard** — Challenge completion rates, badge distribution, top performers

### Frontend Application

| Route | Module | Permission Gate |
|-------|--------|-----------------|
| `/` | Executive Dashboard | `dashboard:read` |
| `/environmental` | Environmental Dashboard | `carbon:read` |
| `/social` | Social Dashboard | `csr:read` |
| `/governance` | Governance Dashboard | `policies:read` |
| `/gamification` | Gamification Dashboard | `challenges:read` |
| `/login` | Authentication | Public |

- Responsive layout with mobile navigation
- Dark/light theme toggle
- Permission-gated sidebar navigation
- Loading skeletons, empty states, and retryable error states
- Recharts visualizations per module
- TanStack Query for server state with cache invalidation on mutations

---

## Architecture

### Style

**Modular monolith** with feature-based boundaries. Each module is self-contained and communicates through defined service interfaces and a lightweight domain event bus.

### Layering

```
Router  →  Service  →  Repository  →  Database
              ↓
         Validators, Events, Activity Log
```

| Layer | Responsibility |
|-------|----------------|
| Router | HTTP routing, request parsing, response formatting |
| Service | Business rules, orchestration, authorization context |
| Repository | Data access, query composition, pagination |
| Models | SQLAlchemy ORM mappings and enum definitions |
| Schemas | Pydantic request/response contracts |

### Cross-Cutting Concerns

- **Authentication middleware** — JWT validation on every request
- **RBAC middleware** — Permission decorator (`@rbac_permissions`) on all business endpoints
- **Exception handlers** — Consistent error codes (401, 403, 404, 409, 422, 500)
- **Request context** — Correlation IDs and structured JSON logging
- **Shared validators** — Enum parsing, pagination, and common filter utilities

### Database Schema (6 Migrations)

| Revision | Scope |
|----------|-------|
| `001_initial_foundation` | Organizations, departments, employees, users, roles, permissions, refresh tokens, activity logs |
| `002_environmental_tables` | Emission factors, carbon transactions, environmental goals, product ESG profiles |
| `003_social_tables` | CSR activities, employee participations |
| `004_governance_tables` | Policies, acknowledgements, audits, compliance issues |
| `005_gamification_tables` | Challenges, participations, badges, employee badges, rewards, redemptions |
| `006_activity_logs_idx` | Index on `activity_logs.created_at` for dashboard feed performance |

### Repository Layout

```text
ecosphere-esg-platform/
├── backend/
│   ├── app/
│   │   ├── auth/              # Authentication, RBAC, session
│   │   ├── core/              # Config, database, security, logging, events
│   │   ├── modules/
│   │   │   ├── dashboard/
│   │   │   ├── environmental/
│   │   │   ├── social/
│   │   │   ├── governance/
│   │   │   └── gamification/
│   │   ├── shared/            # Exceptions, middleware, pagination, validators
│   │   └── tests/             # Integration tests per module
│   ├── alembic/
│   └── scripts/seed_data.py
├── frontend/
│   └── src/
│       ├── app/               # Router, layouts, guards
│       ├── modules/           # Feature pages, hooks, API clients
│       └── shared/            # UI components, API client, hooks
├── docker-compose.yml
└── .github/workflows/ci.yml
```

---

## Tech Stack

### Backend

| Component | Technology |
|-----------|------------|
| Runtime | Python 3.12 |
| Framework | FastAPI 0.115 |
| ORM | SQLAlchemy 2.x |
| Database | PostgreSQL 16 |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Authentication | JWT (python-jose), bcrypt password hashing |
| HTTP server | Uvicorn |
| Linting | Ruff |
| Type checking | mypy (strict) |
| Testing | pytest |

### Frontend

| Component | Technology |
|-----------|------------|
| Framework | React 19 |
| Language | TypeScript 5.7 |
| Build | Vite 6 |
| Styling | TailwindCSS 3, shadcn/ui (Radix primitives) |
| State | TanStack Query 5 |
| Routing | React Router 7 |
| Charts | Recharts |
| Forms | React Hook Form + Zod |
| Icons | Lucide React |

### Infrastructure

| Component | Technology |
|-----------|------------|
| Containers | Docker Compose (PostgreSQL, backend, frontend) |
| CI | GitHub Actions (backend + frontend jobs) |
| API docs | OpenAPI / Swagger (disabled in production) |

---

## Business Workflows

### Carbon Management (Environmental)

1. ESG Manager maintains emission factor catalog (source type, unit, CO₂ factor).
2. Department users or managers record carbon transactions linked to a factor and department.
3. System auto-calculates `quantity × co2_factor` emission values.
4. Environmental goals track department progress toward reduction targets.
5. Product ESG profiles score individual products on carbon, recyclability, and supplier metrics.
6. Analytics aggregate trends, top sources, and department rankings for the executive dashboard.

### CSR Engagement (Social)

1. HR Manager creates CSR activities with category, department, points, and optional evidence requirement.
2. Employees join activities and submit participation with optional proof.
3. Managers approve or reject submissions; approved participations award points.
4. Analytics surface participation rates and department engagement trends.

### Compliance & Governance

1. ESG Manager publishes policies with version and effective date.
2. Employees acknowledge policies; system records attestation timestamp.
3. Auditors plan and complete department audits.
4. Compliance issues are raised with severity and due date; overdue items are auto-flagged.
5. Issues progress through Open → In Progress → Overdue → Closed lifecycle.
6. Governance score reflects policy completion, audit status, and issue resolution.

### Sustainability Gamification

1. ESG/HR Manager creates challenges with XP value, difficulty, deadline, and evidence rules.
2. Employees join active challenges before the deadline.
3. Employees submit progress and proof; managers approve or reject.
4. Approved participations award XP and trigger badge evaluation.
5. Badges unlock automatically when `total_xp` or `approved_challenges` thresholds are met.
6. Employees redeem rewards from the catalog using accumulated XP.
7. Leaderboards rank employees and departments by XP and badge count.

### Executive Reporting (Dashboard)

1. Authenticated user with `dashboard:read` accesses the executive dashboard.
2. System aggregates Environmental, Social, Governance, and Gamification analytics.
3. Composite ESG score is computed from available pillar scores.
4. Quick actions are filtered by the user's effective permissions.
5. Recent activity and notifications surface cross-module events.

---

## Security

### Authentication

- Bcrypt password hashing with per-user salts
- Short-lived JWT access tokens (configurable, default 60 minutes)
- Long-lived refresh tokens (configurable, default 7 days) stored as SHA-256 hashes
- Refresh token rotation on every refresh request
- Token revocation on logout

### Authorization

- Server-side RBAC on every business endpoint via `require_permission` dependency
- Frontend permission checks are UI-only; all enforcement is backend
- Five roles with least-privilege defaults (Employee has participate/read scope only)
- Session endpoint requires `dashboard:read` permission

### Production Hardening

- JWT secret and database URL validation rejects defaults when `ENVIRONMENT=production`
- OpenAPI documentation (`/docs`, `/redoc`) disabled in production
- CORS origins configurable via environment variable
- Structured JSON logging with request correlation IDs
- Global exception handler prevents raw stack traces in API responses

### Input Validation

- Pydantic schemas on all request bodies
- Enum query parameter validation returns 422 instead of database errors
- Badge unlock rules validated against allowed rule types and non-negative thresholds
- Business rule validators for challenge deadlines, evidence requirements, and reward redemption

---

## Performance

### Query Optimization

- Batch badge count queries for leaderboards (eliminates N+1 per employee)
- Batch badge ID lookup for badge evaluation (single query per employee)
- Single leaderboard fetch on dashboard (shared for top performers and XP leaderboard)
- Indexed columns on foreign keys, status fields, transaction dates, and activity log timestamps

### Pagination

- All list endpoints support `page`, `page_size`, `search`, `sort`, and `order` parameters
- Default page size of 20 with maximum of 100
- Pagination metadata included in every list response

### Frontend

- Route-level code splitting via React lazy loading
- TanStack Query caching with targeted invalidation on mutations
- Production build with tree-shaking (Vite)

---

## Testing Summary

### Results

| Suite | Tests | Status |
|-------|-------|--------|
| Health | 1 | Pass |
| Authentication | 7 | Pass |
| Dashboard | 6 | Pass |
| Environmental | 10 | Pass |
| Social | 7 | Pass |
| Governance | 8 | Pass |
| Gamification | 8 | Pass |
| **Total** | **47** | **47 passed, 0 failed** |

### Coverage Areas

- Authentication flows: login, refresh rotation, logout revocation, profile, session RBAC
- CRUD lifecycles for emission factors, carbon transactions, goals, product profiles
- CSR activity and participation approval workflows
- Policy acknowledgements, audit completion, compliance issue overdue flagging
- Challenge join/submit/approve, badge unlock, reward redemption, leaderboards
- Dashboard aggregation across all pillars
- Permission enforcement (401/403 on unauthenticated and unauthorized access)

### Quality Gates (CI)

- Backend: `ruff check app`, `mypy app`, `alembic upgrade head`, `pytest`
- Frontend: `eslint`, `tsc --noEmit`, `vite build`

### Test Infrastructure

- PostgreSQL integration tests with transactional rollback per test
- Shared fixtures for authenticated admin tokens and test entities
- Isolated test database session injected via FastAPI dependency override

---

## Demo Seed Data

Running `python -m scripts.seed_data --reset` populates:

| Entity | Count |
|--------|-------|
| Departments | 8 |
| Employees | 50 |
| Emission factors | 12 |
| Carbon transactions | 100 |
| Environmental goals | Per department |
| Product ESG profiles | 10 |
| CSR activities | 30 |
| CSR participations | 200 |
| Policies | 25 |
| Policy acknowledgements | Sample set |
| Audits | 15 |
| Compliance issues | 35 |
| Challenges | 25 |
| Challenge participations | 200 |
| Badges | 40 |
| Rewards | 25 |
| Reward redemptions | Sample set |
| Activity logs | 40 |

**Default accounts:**

- Admin: `admin@ecosphere.local` / `ChangeMe123!`
- Employees: `firstname.lastname#@ecosphere.local` / `Employee123!`

---

## Known Limitations

| Area | Limitation |
|------|------------|
| Reports module | Not implemented; `reports:read` and `reports:export` permissions exist but no report generation UI or export endpoints |
| AI module | Not implemented; blueprint defines provider abstraction but no LLM integration |
| Administration | Department/category CRUD and ESG settings APIs defined in blueprint but not exposed |
| File uploads | Proof/evidence fields accept string paths only; no upload service or cloud storage integration |
| Multi-tenancy | Single organization per deployment; organization scoping exists in schema but not in application logic |
| Real-time | No WebSocket or SSE; dashboard requires manual refresh or query invalidation |
| Email notifications | Domain events are logged but no email/push notification delivery |
| Refresh token collision | Tokens issued within the same second for the same user produce identical JWTs (edge case under high concurrency) |
| README scope | Root `README.md` foundation scope section is outdated relative to implemented modules |

---

## Future Improvements

### Near Term

- **Reports module** — PDF/Excel export, regulatory report templates (GRI, SASB, TCFD)
- **File upload service** — Cloudinary/S3 abstraction for challenge and CSR evidence
- **Administration UI** — Department, user, and ESG configuration management
- **Refresh token uniqueness** — Add `jti` (JWT ID) claim to guarantee distinct refresh tokens
- **README update** — Align documentation with implemented module scope

### Medium Term

- **AI insights module** — Provider-agnostic LLM integration for ESG recommendations and anomaly detection
- **Config module** — Runtime ESG scoring weights instead of hardcoded pillar percentages
- **Multi-organization support** — Tenant isolation at query and middleware level
- **Notification service** — Email and in-app delivery for domain events
- **Audit log export** — Compliance-grade activity log reporting

### Long Term

- **Microservice extraction** — Gamification or reporting as independent services when scale demands
- **External integrations** — ERP carbon data feeds, HRIS employee sync, sustainability data providers
- **Advanced analytics** — Predictive emissions forecasting, benchmark comparisons
- **Mobile application** — Native or PWA for employee challenge and CSR participation
- **SSO / OIDC** — Enterprise identity provider integration alongside local authentication

---

## Upgrade Instructions

### New Installation

```bash
./scripts/install.sh
cd backend && alembic upgrade head
python -m scripts.seed_data --reset   # optional demo data
```

### Upgrading from Pre-1.0 Foundation

```bash
cd backend
alembic upgrade head
pip install -r requirements.txt
cd ../frontend && npm install && npm run build
```

### Production Checklist

- [ ] Set `ENVIRONMENT=production`
- [ ] Configure strong `JWT_SECRET_KEY` (minimum 32 characters)
- [ ] Configure production `DATABASE_URL`
- [ ] Set `CORS_ORIGINS` to allowed frontend domains
- [ ] Change default admin password
- [ ] Verify OpenAPI docs are inaccessible (`/docs` returns 404)
- [ ] Run `pytest` and `npm run build` before deploy

---

## References

- **Architecture blueprint:** `SYSTEM_BLUEPRINT.md`
- **Setup guide:** `README.md`
- **API documentation:** `http://localhost:8000/docs` (development only)

---

*EcoSphere Enterprise ESG Platform — Proprietary. All rights reserved.*
