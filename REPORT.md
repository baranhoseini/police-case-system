<div style="font-family: Inter, 'Segoe UI', Vazirmatn, 'Helvetica Neue', Arial, sans-serif; line-height: 1.65; font-size: 16px;">

# Police Case System —  Report (Fall 2025 / 1404)

## 1) Repository, stack, and overall structure

- **Backend:** Django REST Framework (DRF)  
- **Frontend:** React (Vite)  
- **DevOps / DB:** Docker Compose + PostgreSQL  
- Key backend links (Swagger/OpenAPI/Admin) are documented in the project README.

> Repository: https://github.com/baranhoseini/police-case-system  
> README: https://raw.githubusercontent.com/baranhoseini/police-case-system/main/README.md

---

## 2) Development strategy (branch-based workflow)

Main implementation and integration work was done through feature branches and then merged into the mainline. The primary branches used for development are visible in the repository Branches list, including:

- `frontend`
- `feature/kimia/domain-backend`
- `feature/baran/*`
- `debuging-frontend-matching-backend`
- `frontend-tests`

> Branch list: https://github.com/baranhoseini/police-case-system/branches/all

---

# 3) Checkpoint 1 — Backend (DRF)

## 3.1) Entities and relationships

**Implemented in branches:**  
- `feature/baran/backend-bootstrap`, `feature/baran/cases-evidence-core`, `feature/baran/rewards-mostwanted-stats`, `feature/kimia/domain-backend`

**Functionality:**
- **Case** supports the statuses: `DRAFT / UNDER_REVIEW / OPEN / CLOSED / INVALIDATED`.
- **Crime level** is stored as `crime_level` (1..4) where **critical = 4**. The `is_critical` property is derived from level 4.
- **Multiple complainants per case** are supported via `CaseComplainant` with statuses `PENDING / APPROVED / REJECTED`, a cadet message, and review metadata (reviewed by / reviewed at). Uniqueness is enforced per `(case, user)`.
- **Complaint** is linked to Case (One-to-One) and has a strike/revision mechanism used to invalidate a case after repeated incorrect submissions.
- **CrimeSceneReport** is linked to Case (One-to-One) and stores witness contact data plus approval metadata.
- **Detective Board** is modeled with `DetectiveBoard`, `DetectiveBoardItem`, and `DetectiveBoardLink`, enabling persistent board items with positional coordinates and links between items.

---

## 3.2) Registration & login

**Implemented in branches:**  
- `feature/baran/auth-jwt`  
- Contract tests added in CP1

**Functionality:**
- Registration accepts the project-required identity fields (e.g., username/password/email/phone/first_name/last_name/national_id), enforced by contract tests.
- Login is JWT-based, and auth flows are validated by backend spec tests.

---

## 3.3) Error handling and standardized responses

**Implemented in branches:**  
- `feature/baran/auth-jwt` and subsequent backend refinements

**Functionality:**
- Invalid inputs and missing resources are handled with appropriate `400/404` responses and consistent error messaging patterns (e.g., `detail`), enabling predictable UI error handling.

---

## 3.4) Role-Based Access Control (RBAC) + role changeability without code changes

**Implemented in branches:**  
- `feature/baran/auth-jwt`, `feature/baran/rbac-crud`, `feature/kimia/domain-backend`  
- Additional CP1 spec tests cover auth/RBAC behaviors

**Functionality:**
- Roles are **managed as data** (create/update/delete) without changing code.
- Role enforcement is applied on sensitive endpoints via role checks/permissions.
- Access rules are explicitly enforced on key business endpoints (e.g., rewards lookup accessibility for police roles).

---

## 3.5) Case creation via complaint (Complaint → review → case creation)

**Implemented in branches:**  
- `feature/kimia/domain-backend`  
- Scenario/spec tests in CP1

**Functionality (step-by-step):**
1) A complainant submits a complaint → a `Complaint` record is created.
2) A cadet can return the complaint with a **feedback message** for correction.
3) Resubmissions increase the **revision/strike counter**.
4) After **3 incorrect submissions**, the associated case (if created) is set to `INVALIDATED`.
5) Contract/spec tests validate the end-to-end flow.

---

## 3.6) Case creation via crime scene report (Crime Scene → approval)

**Implemented in branches:**  
- `feature/kimia/domain-backend`

**Functionality:**
- A `CrimeSceneReport` is created and attached to a case, storing report text and witness identification data.
- Approval state and audit metadata are recorded (`is_approved`, `approved_by`, `approved_at`).

---

## 3.7) Evidence (all required evidence types + critical constraints)

**Implemented in branches:**  
- `feature/baran/cases-evidence-core`, `feature/kimia/domain-backend`  
- Evidence spec tests in CP1

**Functionality:**
- All evidence items include core fields such as `title`, `description`, timestamps, and `created_by`.
- Evidence supports types: `GENERIC`, `MEDICAL`, `VEHICLE`, `ID_DOC`, `WITNESS`.
- **Vehicle evidence constraint:** plate and serial **cannot both exist**, and **at least one must exist**.
- **Medical evidence constraint:** requires at least one image (`image_url` or at least one in `image_urls`).
- **ID document evidence:** supports arbitrary key-value fields stored in a JSON/dict field.
- **Witness evidence:** requires either a transcription or at least one media URL.

---

## 3.8) Case solving, interrogation, decision-making, and trial

**Implemented in branches:**  
- `feature/kimia/domain-backend`

**Functionality:**
- **SolveRequest:** detectives submit solve/detain requests; sergeants approve/reject. Uniqueness prevents multiple simultaneous submitted requests per case.
- **Interrogation:** both detective and sergeant assign a score **1..10** for each suspect per case; uniqueness is enforced for `(case, suspect)`.
- **CaptainDecision:** captains record the final decision; for critical cases, a chief approval pathway exists.
- **Trial:** judges register verdict (`GUILTY/INNOCENT`) and punishment details (title/description).

---

## 3.9) Notifications

**Implemented in branches:**  
- `feature/kimia/domain-backend`

**Functionality:**
- Case notifications are stored per case and receiver, with typed events (e.g., `EVIDENCE_ADDED`) and read tracking (`read_at`).

---

## 3.10) Suspects, Most Wanted, ranking, and reward calculation

**Implemented in branches:**  
- `feature/baran/rewards-mostwanted-stats`  
- Stabilization/refinement in `feature/kimia/domain-backend`

**Functionality:**
- A suspect becomes **Most Wanted** after at least **30 days** of being wanted.
- Ranking score is computed as `max(Lj) * max(Di)` (maximum wanted-days factor × maximum crime-degree factor).
- Reward amount is computed as `rank_score * 20,000,000` (Rial).

---

## 3.11) Rewards (Tip → officer review → detective approval → unique code → lookup)

**Implemented in branches:**  
- Rewards initiation in `feature/baran/rewards-mostwanted-stats`  
- Completed/standardized in `feature/kimia/domain-backend`

**Functionality (step-by-step):**
1) Authenticated citizen submits a tip: `POST /api/rewards/tips/submit/`
2) Officer performs preliminary review (approve/reject + note): `POST /api/rewards/tips/<tip_id>/officer-review/`
3) Detective performs final approval and a **unique_code** is issued: `POST /api/rewards/tips/<tip_id>/detective-approve/`
4) Police staff can verify and retrieve the reward by **(citizen_national_id + unique_code)**:  
   `GET /api/rewards/lookup/?citizen_national_id=...&unique_code=...`  
   The lookup returns the **reward amount** and **citizen details**, with access intended for police roles.

---

## 3.12) Bail/Fine payment (optional) + mock gateway

**Implemented in branches:**  
- `feature/baran/backend-tests`

**Functionality:**
- A mock payment gateway flow exists and is covered by CP1 tests.

---

## 3.13) Aggregated statistics

**Implemented in branches:**  
- `feature/baran/rewards-mostwanted-stats`  
- Wired/extended in `feature/kimia/domain-backend`

**Functionality:**
- Aggregated statistics are provided via API for use in the homepage/dashboard (e.g., counts by case status).

---

## 3.14) Swagger/OpenAPI documentation

**Implemented in branches:**  
- `feature/baran/auth-jwt`

**Functionality:**
- Swagger UI and OpenAPI schema are available at:
  - `/api/docs/`
  - `/api/schema/`

---

## 3.15) Backend tests (minimum coverage requirement)

**Implemented in branches:**  
- `feature/baran/backend-tests`

**Functionality:**
- A set of backend spec/contract tests exists under `backend/spec_tests/` to verify authentication and key flows such as case creation and evidence handling.

---

# 4) Checkpoint 2 — Frontend (React)

## 4.1) Required pages + backend integration

**Implemented in branches:**  
- `frontend`

**Functionality (page-by-page):**
- **Home:** system introduction + at least three aggregated statistics (fed by the backend stats endpoint).
- **Login/Registration:** token-based auth integration with the backend.
- **Modular Dashboard:** modules shown based on user roles (role-based UI).
- **Detective Board:** drag/drop board items, manage connections, and export board as an image (PNG).
- **Most Wanted:** display Most Wanted suspects with ranking/reward-related details.
- **Cases & Complaints Status:** list accessible cases/complaints and allow role-dependent actions; includes case detail view.
- **Global Reporting:** a consolidated case report view (targeted for higher roles such as judge/captain/chief).
- **Evidence:** create and review evidence; supports file upload and real API-backed data.

---

## 4.2) Frontend tests + full-stack Docker Compose usage

**Implemented in branches:**  
- `frontend`, `frontend-tests`

**Functionality:**
- Frontend unit tests are configured via `vitest`.
- Integration testing uses Docker Compose and runs the frontend test suite against a live backend API base URL.

---

# 5) Up to 6 NPM packages and justification

1) **react-router-dom** — application routing  
2) **axios** — HTTP client for backend API calls  
3) **@tanstack/react-query** — request caching, loading/error handling, and data synchronization  
4) **react-hook-form** — scalable form handling for auth and domain forms  
5) **zod** — schema-based validation for form inputs and request payloads  
6) **html-to-image** — exporting the detective board to an image (PNG)

---

# 6) Team responsibilities

## Baran
- Established the backend project structure and core DRF configuration (apps/modules layout, settings organization, environment variables, and baseline tooling).
- Implemented JWT-based authentication end-to-end, including token issuance and authenticated request patterns used throughout the system.
- Configured and maintained API documentation endpoints (Swagger/OpenAPI) to support testing, frontend integration, and evaluation.
- Built the RBAC foundation and role management capabilities so roles can be created/updated/deleted and assigned/revoked without changing code.
- Implemented and maintained shared backend utilities (serializers/permissions patterns) that domain features rely on.
- Delivered foundational endpoints for system-wide needs (e.g., aggregated statistics and initial suspects/rewards wiring for dashboards and admin flows).
- Set up Docker/Postgres infrastructure and ensured the backend runs reliably via containerized workflows for consistent development and testing.
- Created and expanded backend spec/contract tests to validate CP1 requirements and protect key business flows (auth, case creation, evidence rules, RBAC access behavior).
- Led API–frontend contract alignment and stabilization work (payload shapes, status codes, and error formats) so UI integration remained smooth during CP2.
- Supported ongoing maintenance: bug-fixing, migrations cleanup, and keeping endpoints stable as domain requirements evolved.



## Kimia
- Implemented complaint-based case creation flow: cadet review, feedback messaging, officer loop-back, and the “3 strikes → invalidation” rule.
- Implemented multi-complainant support and review lifecycle per case (pending/approved/rejected) with proper audit metadata.
- Implemented crime-scene-based case creation with witness identifiers, approval auditing, and state transitions into active investigation states.
- Designed and implemented the investigation pipeline: solve/detain requests, sergeant approvals/rejections, and constraints to prevent duplicate submitted requests.
- Implemented interrogation scoring per suspect per case (detective + sergeant scores from 1–10) and ensured uniqueness/integrity at the data model level.
- Implemented captain decision workflow and ensured critical-crime pathways can require chief validation before escalation.
- Implemented trial workflow to record judge verdicts and punishment details, enabling end-to-end case closure and reportability.
- Hardened the evidence domain with strict validations (vehicle plate/serial XOR, medical image requirements, witness transcription/media rules, ID-doc key–value fields).
- Implemented case notifications for key domain events (e.g., evidence added and review outcomes) to keep detectives informed during investigation.
- Stabilized API contracts and permissions across domain endpoints (cases/evidence/suspects/rewards), including cleanup for consistent frontend integration.



## Melina
- Built the core React (Vite) application structure, routing, shared layouts, and protected routes to cover all required pages.
- Implemented authentication UX (login/register), token storage and logout, and attaching JWT to API requests for authenticated flows.
- Developed a modular, role-aware dashboard so each role sees the correct modules, navigation entries, and workflow entry points.
- Implemented the cases/complaints experience end-to-end: lists, detail views, status rendering, and role-based actions aligned with backend permissions.
- Built the evidence module: create evidence by type, upload/attach media, preview items, and surface API validation errors in a user-friendly way.
- Delivered the Detective Board UI: drag & drop positioning, create/remove links, persist board state, and export PNG for attaching to reports.
- Implemented the Most Wanted page consuming backend ranking and reward outputs, with a UI that scales to many entries and highlights top targets.
- Implemented a global reporting view for high-authority roles, showing consolidated case metadata, evidence, suspects, complainants, and involved staff.
- Improved UI/UX quality: navigation polish, responsive layouts, loading/empty states, and consistent reusable components across pages.
- Prepared the frontend for reliability: vitest unit tests, integration test readiness, and smooth Docker Compose full-stack runs.





---

# 7) Development conventions (contracts)

## 7.1) Naming conventions
- **Backend (Python/Django):** snake_case for variables/functions, PascalCase for classes, clear domain-oriented model names (e.g., Case, Complaint, Evidence).
- **API:** consistent REST-style paths and resource naming; actions exposed only where the workflow requires them.
- **Frontend (React):** component- and feature-oriented structure; reusable UI components for repeated patterns (forms, lists, detail panels).

## 7.2) Git workflow and commit message style
- Feature work was done on dedicated branches and merged after review/testing.
- Commit messages were kept descriptive and scope-oriented (feature/fix/refactor style), so reviewers can track changes and their intent quickly.

## 7.3) API contracts and integration rules
- The frontend relies on a stable API contract:
  - predictable status codes (`2xx/4xx/5xx`)
  - consistent error payload shapes
  - role-based access enforced on the backend (frontend does not “fake” permissions)
- Breaking changes were handled through alignment/stabilization work before merging to mainline.

---

# 8) Project management approach (task production & division)

- Work was organized around the two official checkpoints:
  - **CP1:** backend-first delivery (entities, workflows, permissions, documentation, tests).
  - **CP2:** frontend delivery (pages, UX, API integration, full-stack dockerization, tests).
- Tasks were produced by translating each requirement in the specification into:
  - a domain entity (model + relations),
  - a workflow step (endpoints + permissions),
  - and an acceptance check (spec/contract tests and/or UI verification).
- Integration was done iteratively:
  - early API scaffolding → UI wiring → contract alignment → test hardening → final polish.

---

# 9) Key entities and why they exist (rationale)

- **User / Roles / UserRole (RBAC):**  
  Enables dynamic role assignment and strict access control without code changes; required to model police ranks and citizen roles flexibly.

- **Case:**  
  The central unit of work that ties together complaints, crime-scene reports, evidence, suspects, and the judicial pipeline. Case statuses encode the workflow state.

- **Complaint:**  
  Represents citizen-initiated intake and supports review cycles, feedback, and the “3 strikes → invalidation” rule.

- **CaseComplainant:**  
  Supports multiple complainants per case with independent review decisions and audit metadata.

- **CrimeSceneReport:**  
  Represents police-initiated intake from observing/reporting a crime scene, including witness identifiers and approval traceability.

- **Evidence:**  
  Stores all evidence types (medical, vehicle, ID documents, witness) and enforces domain constraints to prevent invalid records.

- **DetectiveBoard / Items / Links:**  
  Provides persistence for the detective board so the frontend can implement drag/drop, linking, and export without heavy backend changes later.

- **Suspect (+ Most Wanted ranking):**  
  Models wanted status and allows ranking + reward computation for public “Most Wanted” display.

- **Rewards (tips + unique code):**  
  Models citizen tips, officer review, detective approval, and payout verification using a unique code + national ID lookup.

- **SolveRequest / Interrogation / CaptainDecision / Trial:**  
  Captures the end-to-end investigation and judicial decision chain as required: approvals, scoring, escalation, verdict, and punishment.

---

# 10) AI usage — strengths and weaknesses

## 10.1) Strengths (how it helped)
- Faster scaffolding for repetitive code (serializers, basic views, data validation patterns, and UI boilerplate).
- Quick iteration on alternative designs (API shape options, model relationship sketches, UI layout ideas).
- Accelerated documentation drafting (summaries of workflows and module responsibilities).

## 10.2) Weaknesses (what still required careful review)
- Domain edge-cases often need human validation (e.g., XOR constraints, multi-step approval paths, and role boundary conditions).
- AI output can look correct but miss subtle specification requirements (e.g., exact workflow routing and audit details).
- Code quality still depends on refactoring and consistency work (naming, error format standardization, and contract stability).

**Mitigation:** all AI-assisted output was reviewed, tested, and adapted to match the specification and the project’s RBAC rules.

---

# 11) Requirements evolution — initial vs final needs (decisions & trade-offs)

## 11.1) Initial needs
- Establish a maintainable backend foundation: entities, relationships, and RBAC as the system backbone.
- Implement the required workflows in a testable way with stable API contracts and clear error handling.
- Prepare the system for CP2 by designing backend support for complex UI parts (especially the detective board and reporting).

## 11.2) Final needs (after CP2 integration)
- Deliver a complete role-based UI that covers all required pages and user journeys.
- Ensure full-stack operability with Docker Compose for consistent evaluation environments.
- Improve reliability and confidence via automated tests (backend contract tests + frontend unit/integration readiness).
- Refine UX and integration details (loading/error states, consistent navigation, and stable request patterns).

## 11.3) Key decisions (pros/cons)
- **DRF + React (Vite):** clear separation of concerns; faster UI iteration; requires careful API contract management.
- **RBAC as data (changeable roles):** meets the specification’s dynamic role requirement; requires robust admin/role endpoints and thorough testing.
- **React Query for data fetching:** improves caching/loading/error handling; introduces patterns that must be applied consistently across pages.
- **Strict domain validations (evidence & workflows):** prevents invalid states early; increases validation logic complexity but reduces downstream bugs.


</div>
