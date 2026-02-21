# WP-F2025 Project (Spec-aligned)

This repository contains:
- `backend/`: Django REST API (JWT auth, RBAC, cases, evidence, detective board)
- `frontend/`: Vite + React (TypeScript)

## Quick start (local)

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_roles  # optional: create default roles
python manage.py runserver
```

Backend runs on http://127.0.0.1:8000

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Frontend runs on http://127.0.0.1:5173

## Notes
- Registration requires: username, first_name, last_name, email, phone, national_id, password.
- Login supports identifier = username/email/phone/national_id + password.
- Evidence types are mapped to backend evidence_type choices (ID_DOC, VEHICLE, MEDICAL, GENERIC/WITNESS).
