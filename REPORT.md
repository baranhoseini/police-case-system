<div style="font-family: Inter, 'Segoe UI', Vazirmatn, 'Helvetica Neue', Arial, sans-serif; line-height: 1.7; font-size: 16px;">

# Police Case System — Report (Fall 2025 / 1404)

---

## 1) Repository, stack, and overall structure

- **Backend:** Django REST Framework (DRF)  
- **Frontend:** React (Vite)  
- **DevOps / DB:** Docker Compose + PostgreSQL  
- API documentation and operational notes (Swagger/OpenAPI, run commands, environment variables) are maintained in the project README.

---

## 2) Development strategy (branch-based workflow)

Development followed a feature-branch workflow:
- Backend foundation and infrastructure were built on dedicated backend feature branches.
- Domain/business workflows were implemented on a dedicated domain backend branch.
- UI and integration with the API were implemented on a dedicated frontend branch.
- Stabilization work (API–UI contract alignment, test hardening) was done on dedicated integration/testing branches.

(Primary branches are visible in the repository Branches list.)

---

# 3) Checkpoint 1 — Backend (DRF)

## 3.1) Entities and relationships

**Implemented in branches:**  
- `feature/baran/backend-bootstrap`, `feature/baran/cases-evidence-core`, `feature/baran/rewards-mostwanted-stats`, `feature/kimia/domain-backend`

**Functionality:**
- **User & Roles (RBAC):**  
  - Roles are stored as data entities and can be managed dynamically (create/update/delete roles and assign roles to users).  
  - Endpoints enforce role-based access consistently across sensitive actions (review/approval flows, lookup endpoints, and administrative operations).

- **Case lifecycle (core business object):**  
  - Each case has a defined lifecycle and supports the statuses:  
    `DRAFT / UNDER_REVIEW / OPEN / CLOSED / INVALIDATED`.  
  - Cases carry critical fields required by the specification (e.g., title/description, crime level) and maintain audit trails for actions and approvals.

- **Crime severity (levels 1–4):**  
  - Crime severity is stored as `crime_level` in the range `1..4`.  
  - **Critical crimes** are represented by level **4** and are used to activate stricter approval requirements in downstream workflows.

- **Multiple complainants per case:**  
  - A case supports multiple complainants via `CaseComplainant`, with per-complainant review status:  
    `PENDING / APPROVED / REJECTED`  
  - Cadet feedback is stored (message/note), and review metadata is recorded (reviewed_by/reviewed_at).  
  - Duplicate complainant assignment to the same case is prevented (unique `(case, user)`).

- **Complaint as a formal intake object:**  
  - A complaint is linked to a case (One-to-One) and carries a revision/strike mechanism to support the “3 incorrect submissions → invalidate” rule.

- **Crime scene reporting:**  
  - A `CrimeSceneReport` is linked to a case (One-to-One) and stores witness contact identifiers plus approval metadata.

- **Detective Board data model (backend support):**  
  - Detective Board is represented by `DetectiveBoard`, `DetectiveBoardItem`, and `DetectiveBoardLink`, enabling:
    - Persistent board items and their positions (`x`, `y`)  
    - Connections between board items (links)  
    - Reliable retrieval and saving so the frontend board can remain lightweight and responsive.

---

## 3.2) Registration & login

**Implemented in branches:**  
- `feature/baran/auth-jwt` + CP1 contract tests

**Functionality:**
- Registration is implemented to accept identity information required by the specification (username/password plus personal identity fields).  
- Login is **JWT-based**, returning tokens that can be used to authenticate subsequent API calls.  
- API contracts are validated via backend spec/contract tests to reduce integration ambiguity with the frontend.

---

## 3.3) Error handling and standardized responses

**Implemented in branches:**  
- `feature/baran/auth-jwt` and later backend refinements

**Functionality:**
- Invalid payloads and business-rule violations return structured `400` errors with clear messages.  
- Missing resources return `404` errors with predictable message formats.  
- This standardization allows the frontend to show accurate user-facing error messages (e.g., on invalid lookup codes, unauthorized access, or incomplete submissions).

---

## 3.4) Role-Based Access Control (RBAC) + role changeability without code changes

**Implemented in branches:**  
- `feature/baran/auth-jwt`, `feature/baran/rbac-crud`, `feature/kimia/domain-backend` (+ CP1 tests)

**Functionality:**
- Roles are fully data-driven and manageable without editing code:
  - Add a new role
  - Modify an existing role
  - Remove a role
  - Assign/revoke roles from users
- Role checks are enforced across endpoints so that:
  - Citizens cannot perform police-only actions  
  - Cadets can perform cadet-only review steps  
  - Detective/Sergeant/Captain/Chief can perform higher-authority decisions  
- Critical business endpoints (e.g., rewards lookup, officer review, detective approval) are permissioned to match the specification.

---

## 3.5) Case creation via complaint (Complaint → Cadet review → Officer review → Case formed)

**Implemented in branches:**  
- `feature/kimia/domain-backend` + scenario/spec tests in CP1

**Functionality (step-by-step):**
1) **Citizen submits complaint:**  
   A complaint is created and associated with a case intake record.
2) **Cadet (initial validation):**  
   The cadet reviews the complaint. If incomplete/incorrect:
   - The cadet returns it to the citizen with a **feedback message** describing what is wrong.
3) **Officer review:**  
   After cadet validation, the complaint proceeds upward for officer review before the case becomes fully active.
4) **Officer-to-cadet loop on defects:**  
   If an officer finds issues, the complaint is routed back to cadet review rather than directly to the citizen.
5) **Three strikes rule:**  
   Each incorrect resubmission increments the strike counter.  
   If strikes reach **3**, the case is marked **INVALIDATED** and is removed from further review progression.

---

## 3.6) Case creation via crime scene report (Police report → Approval → Case OPEN)

**Implemented in branches:**  
- `feature/kimia/domain-backend`

**Functionality:**
- Police roles (excluding cadet) can create a case by reporting a crime scene:
  - The report includes narrative details and witness identifiers (phone/national ID) for follow-up.
- Approval rules:
  - A superior role can approve the report (approval is audited with who/when).
  - Once approved, the case proceeds into an active state (`OPEN`) according to the workflow design.

---

## 3.7) Evidence (required evidence types + strict constraints)

**Implemented in branches:**  
- `feature/baran/cases-evidence-core`, `feature/kimia/domain-backend` + CP1 evidence tests

**Functionality:**
- All evidence records include:
  - `title`, `description`
  - creation timestamp and a registered creator
  - association to a case
- Supported evidence types and required behaviors:
  - **GENERIC:** simple title/description evidence.
  - **MEDICAL:** supports storing medical/biological evidence with one or more images and a later-updatable result field.
  - **VEHICLE:** captures model/color and identifiers with a strict XOR constraint:
    - plate and serial cannot both be present  
    - at least one must be provided
  - **ID_DOC:** stores identity-document data as flexible **key–value** fields (JSON) to support variable document formats.
  - **WITNESS:** supports witness transcription and/or media attachments (audio/video/image URLs).
- Evidence constraints are validated so inconsistent records cannot be saved, preventing downstream workflow errors.

---

## 3.8) Investigation pipeline: solving, interrogation, captain decision, trial

**Implemented in branches:**  
- `feature/kimia/domain-backend`

**Functionality:**
- **Detective board workflow support:**  
  Evidence and notes can be organized into board items and linked, enabling structured reasoning.
- **SolveRequest (Detective → Sergeant):**  
  Detective submits a solve/detain request. Sergeant:
  - approves → arrests/next steps proceed  
  - rejects → returns an explicit rejection state/message and keeps the case open
  Uniqueness prevents multiple simultaneous submitted requests for the same case.
- **Interrogation scoring (Detective + Sergeant):**  
  Both detective and sergeant score each suspect from **1 to 10**, recorded per `(case, suspect)` to prevent duplicates.
- **Captain decision (+ Chief validation for critical cases):**  
  Captain records final decision using case data, evidence, and interrogation scores.  
  If the case is critical (crime level 4), chief approval is required before final escalation.
- **Trial (Judge):**  
  Judge records:
  - verdict (`GUILTY` / `INNOCENT`)
  - punishment title and description (when guilty)
  This ensures the system preserves full judicial outcome information per the specification.

---

## 3.9) Notifications (domain events)

**Implemented in branches:**  
- `feature/kimia/domain-backend`

**Functionality:**
- The backend stores case notifications per receiver with:
  - event type (e.g., evidence added)
  - read tracking (`read_at`)
- This supports the required behavior where new evidence triggers a notification to the responsible detective so ongoing investigations stay updated.

---

## 3.10) Suspects, Most Wanted, ranking, and reward calculation

**Implemented in branches:**  
- `feature/baran/rewards-mostwanted-stats` (core) + `feature/kimia/domain-backend` (stabilization)

**Functionality:**
- When a suspect becomes wanted in a case, wanted duration is tracked.
- **Most Wanted rule:** suspects with **> 30 days** in wanted status appear in Most Wanted.
- **Ranking rule:** computed as `max(Lj) * max(Di)`:
  - `max(Lj)` = maximum wanted days across open cases
  - `max(Di)` = maximum crime degree factor (mapped from crime levels 1–4)
- **Reward amount:** `rank_score * 20,000,000` (Rial), displayed alongside suspect details.

---

## 3.11) Rewards (Tip → Officer review → Detective approval → Unique code → Lookup)

**Implemented in branches:**  
- Initiation in `feature/baran/rewards-mostwanted-stats` + completion in `feature/kimia/domain-backend`

**Functionality (step-by-step):**
1) **Citizen tip submission:**  
   Citizen submits actionable information about a case or suspect.
2) **Officer preliminary review:**  
   Officer rejects invalid tips or forwards valid tips for detective review; a decision note is stored.
3) **Detective approval & code issuance:**  
   Detective approves the tip and the system generates a **unique reward code** for payout.
4) **Lookup for payout verification:**  
   Police staff can lookup a reward using **(citizen_national_id + unique_code)**.  
   The lookup returns:
   - reward amount  
   - citizen information needed for identification/payout  
   Access is restricted to police roles, matching the specification.

---

## 3.12) Bail/Fine payment (optional) + mock gateway

**Implemented in branches:**  
- `feature/baran/backend-tests`

**Functionality:**
- A mock payment flow exists to simulate bail/fine payment, enabling end-to-end validation without a real payment gateway.
- The flow is test-covered to ensure stable behavior during evaluation.

---

## 3.13) Aggregated statistics

**Implemented in branches:**  
- `feature/baran/rewards-mostwanted-stats` + `feature/kimia/domain-backend`

**Functionality:**
- Aggregated statistics endpoints provide system-level metrics used by the homepage/dashboard:
  - counts of active cases
  - counts of solved/closed cases
  - organizational/user counts (as configured by the system data model)

---

## 3.14) Swagger/OpenAPI documentation

**Implemented in branches:**  
- `feature/baran/auth-jwt`

**Functionality:**
- Swagger UI and OpenAPI schema endpoints are provided:
  - `/api/docs/`
  - `/api/schema/`

---

## 3.15) Backend tests (minimum coverage requirement)

**Implemented in branches:**  
- `feature/baran/backend-tests`

**Functionality:**
- Backend spec/contract tests verify:
  - authentication and token issuance  
  - complaint/case creation flows  
  - evidence creation and constraints  
  - RBAC behaviors for key endpoints  

---

# 4) Checkpoint 2 — Frontend (React)

## 4.1) Required pages + API integration

**Implemented in branches:**  
- `frontend`

**Functionality (page-by-page):**
- **Home:**  
  - shows a brief system introduction  
  - displays at least **three** aggregated statistics from backend APIs (cases, statuses, counts)
- **Login / Registration:**  
  - authenticates via backend auth endpoints  
  - stores tokens and attaches them to subsequent API requests
- **Modular Dashboard:**  
  - renders modules conditionally based on roles  
  - examples: Detective Board module visible to detectives; cadet-specific review modules visible to cadets
- **Detective Board:**  
  - supports drag & drop positioning of items  
  - supports connecting items (links) and removing links  
  - supports exporting the board to an image (PNG) for attaching to reports
- **Most Wanted:**  
  - displays most-wanted suspects with ranking and reward information  
  - supports list and detail views appropriate to the UI design
- **Cases & Complaints Status:**  
  - lists accessible cases/complaints based on role rules  
  - supports detail view with role-based actions (review/approve/reject/status changes)
- **Global Reporting:**  
  - shows a consolidated case report intended for higher roles (judge/captain/chief), including key case metadata, evidence summaries, suspects, and involved parties
- **Evidence:**  
  - supports adding evidence by type  
  - supports uploading/associating images/media  
  - supports reviewing evidence lists per case

---

## 4.2) Frontend tests + full-stack Docker Compose usage

**Implemented in branches:**  
- `frontend`, `frontend-tests`

**Functionality:**
- Frontend unit testing is configured via `vitest`.
- Integration testing runs against a live backend using Docker Compose, validating API contracts from the UI side and ensuring the full stack works together.

---

# 5) Up to 6 NPM packages and justification

1) **react-router-dom** — application routing  
2) **axios** — HTTP client for backend API calls  
3) **@tanstack/react-query** — caching, loading/error handling, data synchronization  
4) **react-hook-form** — scalable form management for auth and domain workflows  
5) **zod** — schema-based validation for inputs and payloads  
6) **html-to-image** — exporting the detective board to an image (PNG)

---

# 6) Team responsibilities

## Baran
- Established the backend project structure and core DRF configuration (apps/modules layout, settings organization, environment variables, and baseline tooling).
- Implemented JWT-based authentication end-to-end, including token issuance and authenticated request patterns used throughout the system.
- Configured and maintained API documentation endpoints (Swagger/OpenAPI) to support testing, frontend integration, and evaluation.
- Built the RBAC foundation and role management capabilities so roles can be created/updated/deleted and assigned/revoked without changing code.
- Implemented and maintained core backend modules and shared utilities that other domain features depend on, including baseline case/evidence scaffolding and shared serializers/permissions patterns.
- Delivered foundational endpoints for system-wide features (such as aggregated statistics and initial suspects/rewards wiring) that power the homepage/dashboard and administrative flows.
- Set up Docker/Postgres infrastructure and ensured the backend can run reliably via containerized workflows for consistent development and testing.
- Created and expanded backend spec/contract tests to validate CP1 requirements and protect key business flows (auth, case creation, evidence rules, RBAC access behavior).
- Led API–frontend contract alignment and stabilization work (parameter names, payload shapes, status codes, and error formats) so UI integration remained smooth during CP2.
- Supported ongoing maintenance: bug-fixing, migrations cleanup, and ensuring endpoints remain stable as new domain requirements were added.



## Kimia
- Implemented and stabilized backend **domain workflows** end-to-end, including:
  - Complaint-based and crime-scene-based case creation, review/approval rules, and audit trails
  - Core case state transitions and enforcement of the “3 strikes → invalidation” rule
  - Full investigation pipeline: solve requests, interrogation scoring (1–10), captain decisions, and trial verdict/punishment recording
  - Evidence domain hardening: strict validations, edge-case handling, and schema/migration stabilization
  - Notification mechanics for domain events (notifying detectives on new evidence and review outcomes)
  - Rewards flow completion: officer review, detective approval, unique-code issuance, and lookup contract with correct access control
  - Endpoint cleanup and consistency improvements so the frontend can rely on stable, predictable APIs

## Melina
- Implemented the required frontend pages and navigation structure, ensuring the application covers the full set of required screens (Home, Auth, Dashboard, Cases, Reports, Evidence, Most Wanted, Detective Board).
- Connected the UI to the real backend APIs (not mock data), including authentication, token storage, authenticated requests, and consistent API error handling in the client.
- Built a modular, role-aware dashboard experience so each role sees the correct modules and actions (e.g., detectives see the Detective Board, medical roles see only what they need, citizens see citizen flows).
- Implemented the Cases experience end-to-end: case lists, case detail views, status rendering, and role-based actions (review, approval, progress changes) aligned with backend permissions.
- Implemented the Evidence experience end-to-end: evidence listing per case, evidence creation by type, and media handling (file upload / attaching images or URLs), with validation-friendly UX.
- Delivered the Detective Board UI with key usability features such as drag & drop positioning, link management between items, and exporting the board as an image (PNG) for attaching to investigation reports.
- Implemented the Most Wanted page to display suspects with ranking/reward context, with a UI that can scale to multiple entries and highlight the most important targets.
- Implemented the Global Reporting view intended for high-authority roles, presenting a consolidated summary of each case (metadata, evidence, suspects, and involved parties) for judicial/command review.
- Focused on UX polish and consistency: navigation refinement, layout improvements, and UI cleanups so the system is presentation-ready.
- Prepared the frontend for testing and reliability, including unit/integration test readiness and ensuring the app works correctly when run via Docker Compose with the backend.



</div>
