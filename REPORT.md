<div style="font-family: Inter, 'Segoe UI', Vazirmatn, 'Helvetica Neue', Arial, sans-serif; line-height: 1.65; font-size: 16px;">

# Police Case System — Final Report (Fall 2025 / 1404)

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
- Backend project bootstrapping and core structure (apps/modules layout)
- JWT authentication setup and DRF configuration, plus Swagger/OpenAPI setup
- RBAC foundations and role management APIs
- Core backend entities and Docker/DB infrastructure support
- Adding and extending backend tests, including CP1 scenario/spec coverage
- API contract adjustments to ensure smooth frontend-backend integration

## Kimia
- Implementing and stabilizing the backend **domain flows** end-to-end, including:
  - Complaint-based and crime-scene-based case creation flows and their review/approval mechanics
  - Core state transitions (draft/review/open/invalidated/closed) and the “3 strikes → invalidation” rule
  - The complete investigation pipeline: solve requests, interrogation scoring, captain decisions, and trial verdict/punishment recording
  - Evidence domain hardening: stricter validations, edge-case handling, and schema/migration stabilization
  - Notification mechanics for key domain events (e.g., evidence additions) to support detective workflows
  - Rewards flow completion: officer review + detective approval + unique-code issuance + lookup contract and access control
  - Endpoint cleanup and consistency improvements so the frontend can rely on stable, predictable APIs

## Melina
- Implementing the frontend pages required by the specification (Home/Auth/Dashboard/Cases/Reports/Evidence/MostWanted/DetectiveBoard)
- Replacing mock data with real backend-integrated data flows (auth, cases, evidence, statistics)
- Implementing user-facing features such as evidence upload and detective board export-to-image
- UI/navigation refinements and preparing the frontend for unit and integration testing

</div>
