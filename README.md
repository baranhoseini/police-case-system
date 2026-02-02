# Police Case System

Web Programming course project.

## Tech Stack
- Backend: Django REST Framework (DRF)
- Frontend: React or NextJS

## Repository Structure
```text
/
  backend/
  frontend/
```

---

## Run Backend (Django + DRF)

### Prerequisites
- Python 3.10+ (recommended)
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

### Useful URLs
- Django Admin: http://127.0.0.1:8000/admin/
- Swagger UI: http://127.0.0.1:8000/api/docs/
- OpenAPI schema: http://127.0.0.1:8000/api/schema/

---

## Run Frontend (placeholder)

> Add frontend instructions after the React/Next app is created.

Typical (NextJS):
```bash
cd frontend
npm install
npm run dev
```

---

## Contributing / Workflow (team)
- Work on feature branches: `feature/<name>/<topic>`
- Open PRs and link them to Issues using `refs #<issue>` / `closes #<issue>`
- Avoid squashing PRs if you need commit-count attribution per member.
