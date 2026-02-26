# Police Case System

Web Programming course project.

This README is optimized for **presentation day (Docker-first)**: every command + link you need is here so you don’t have to open ChatGPT.

---

## Tech Stack

- **Backend:** Django + Django REST Framework (DRF)
- **Frontend:** React (Vite)
- **DB (Docker):** PostgreSQL

---

## Repository Structure

```text
/
  backend/
  frontend/
  docker-compose.yml
```

---

## Quick Links (when running)

- **Frontend (UI):** http://localhost:5174  
- **Backend API base:** http://localhost:8000/api  
- **Backend Swagger (API docs):** http://localhost:8000/api/docs/  
- **OpenAPI schema:** http://localhost:8000/api/schema/

---

# ✅ Presentation Path (Recommended): Run Everything with Docker

## Prerequisites

- Docker + Docker Compose installed
- Run commands from the **project root** (folder that contains `docker-compose.yml`)

## Start the full stack (DB + Backend + Frontend)

### Build + start
```bash
docker compose up -d --build
```

### Check status
```bash
docker compose ps
```

### View logs (if needed)
```bash
docker compose logs --tail=120 backend
docker compose logs --tail=120 frontend
docker compose logs --tail=120 db
```

### Stop everything
```bash
docker compose down
```

### Full reset (removes DB volume too)
> Use this if you want a clean demo dataset and don’t care about wiping the DB.
```bash
docker compose down -v
docker compose up -d --build
```

---

## Migrations (Docker)

Run migrations explicitly (safe to run multiple times):
```bash
docker compose exec backend python manage.py migrate
```

---

## Seed demo data (optional but recommended)

If your backend includes seed commands, run:
```bash
docker compose exec backend python manage.py seed_roles
docker compose exec backend python manage.py seed_dev --reset
```

If a seed command is missing, skip this section and demo using whatever data you already have in the UI.

---

## Run Tests (Docker)

### Backend tests (Django)
```bash
docker compose exec backend python manage.py test
```

### Frontend tests (Vitest) — includes REAL backend integration tests
Because tests run **inside the frontend container**, the backend is reachable at `http://backend:8000` (Docker network hostname).

```bash
docker compose exec -e VITE_API_BASE_URL="http://backend:8000/api" frontend npm test
```

✅ This verifies real frontend ↔ backend connectivity from inside Docker.

> Notes:
> - You may see React `act(...)` warnings. These are warnings, not failures.
> - If your Vitest config is set to only run project tests, you should see only `src/__tests__` and `src/__integration__`.

---

## E2E (Playwright) — optional

### Important (Docker Alpine)
If the frontend container uses Alpine, `npx playwright install --with-deps` may fail in Docker (no `apt-get`).  
For presentation day, the simplest approach is:

✅ Keep the stack running in Docker  
✅ Run Playwright **on your host machine** (Mac/Windows/Linux), if you want to show E2E

### Run on your host machine (recommended)
```bash
docker compose up -d --build
```

Then:
```bash
cd frontend
npm install
npx playwright install
npx playwright test
```

---

# Local Development (Optional)

> Not required for presentation if Docker works. Included for completeness.

## Run Backend (Django + DRF) locally

### Prerequisites
- Python 3.10+ recommended
- pip

### 1) Go to backend folder
```bash
cd backend
```

### 2) Create & activate virtual environment

#### Windows (PowerShell)
```bash
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

#### macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3) Install dependencies
```bash
pip install -r requirements.txt
```

### 4) Run migrations
```bash
python manage.py migrate
```

### 5) (Optional) Create admin user
```bash
python manage.py createsuperuser
```

### 6) Start the server
```bash
python manage.py runserver
```

### Useful URLs (local backend)
- Django Admin: http://127.0.0.1:8000/admin/
- Swagger UI: http://127.0.0.1:8000/api/docs/
- OpenAPI schema: http://127.0.0.1:8000/api/schema/

---

## Run Frontend locally (Vite)
```bash
cd frontend
npm install
npm run dev
```

---

# Common Issues & Quick Fixes

### Frontend UI loads but API calls fail
- For the **browser UI**, the API base should usually be:
  - `http://localhost:8000/api`
- For **tests running inside Docker**, use:
  - `http://backend:8000/api`

Check backend logs:
```bash
docker compose logs --tail=200 backend
```

### Backend cannot connect to DB on first boot
Sometimes Postgres isn’t ready before backend migrates.
Fix:
```bash
docker compose restart backend
```

### Port already in use
Default ports:
- Frontend: `5174`
- Backend: `8000`
- Postgres: `5432`

Stop the conflicting service or change ports in `docker-compose.yml`.

---

# Contributing / Workflow (team)

- Work on feature branches: `feature/<name>/<topic>`
- Open PRs and link them to Issues using `refs #<issue>` / `closes #<issue>`
- Avoid squashing PRs if you need commit-count attribution per member.
