# Police Case System

Web Programming course project.

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
