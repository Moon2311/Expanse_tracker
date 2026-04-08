# Spendly — Expense Tracker

Spendly tracks **personal and group expenses**, **splits**, **notifications**, and **chat**. This repository ships a **Django REST API** (`backend/`) and a **React + Vite** SPA (`frontend/`).

| Part | Role | Local URL |
|------|------|-----------|
| **Django API** | JSON API, JWT auth, PostgreSQL | http://127.0.0.1:8000/api/ |
| **React app** | Web UI (proxies `/api` to Django in dev) | http://localhost:5173 |

The API uses its **own user database** (UUID users). If you also run an optional **Flask** app from the repo root (when `app.py` is present), treat it as a **separate** app with its own tables.

---

## Prerequisites

- **Python 3.11+** (3.12 recommended)
- **PostgreSQL** (local or remote)
- **Node.js 18+** and **npm** (frontend)

---

## 1. Clone and configure environment

```bash
git clone <your-repo-url> expense-tracker
cd expense-tracker
```

Copy env templates and edit real values (never commit `.env` — it is listed in `.gitignore`):

```bash
cp .env.example .env
cp .env.example backend/.env
# Or share one file:
# ln -sf ../.env backend/.env
```

Optional frontend override (e.g. production API URL):

```bash
cp frontend/.env.example frontend/.env
```

| You must set | Purpose |
|--------------|---------|
| `DJANGO_SECRET_KEY` | Django signing (generate a long random string) |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | PostgreSQL connection |
| `CORS_ALLOWED_ORIGINS` | Browser origins allowed to call the API (comma-separated) |

If you use the **Flask** app at the root, also set `FLASK_SECRET_KEY` in the root `.env`.

**CI / cloud:** GitHub Actions uses **`GITHUB_TOKEN`** to push the backend Docker image to **GHCR** — nothing to add to `.env`. For Kubernetes, use the same variable **names** as in `.env.example` inside a Secret; see `deploy/kubernetes/backend-secret.example.yaml` (do not commit a filled `backend-secret.yaml`).

Create the database:

```bash
createdb spendly
# or: psql -c "CREATE DATABASE spendly;"
```

If the database name contains spaces, match `DB_NAME` exactly to how PostgreSQL stores it.

---

## 2. Run the Django API

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Ensure **`backend/.env`** exists (section 1).

```bash
python manage.py migrate
python manage.py runserver 8000
```

- API: **http://127.0.0.1:8000/api/**
- Health check: **http://127.0.0.1:8000/healthz**
- Admin (optional): `python manage.py createsuperuser` → http://127.0.0.1:8000/admin/

More endpoint detail: **`backend/README.md`**.

---

## 3. Run the React frontend

Second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**. Dev mode proxies **`/api`** to **http://127.0.0.1:8000**, so keep Django on port **8000**.

Register in the SPA — users are stored by the Django API, not by any optional Flask app.

---

## 4. Optional: Flask app (repo root)

Some trees include a classic **Flask + Jinja** UI (`app.py`, `database/`, `templates/`, …). If those exist:

```bash
cd expense-tracker
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -c "from database import init_db; init_db()"
python app.py
```

Use a root **`.env`** with `FLASK_SECRET_KEY` and the same **`DB_*`** variables. Default port is often **5001** (check `app.py`).

---

## 5. Docker (backend image)

Build and run the API container (PostgreSQL must be reachable from the container; pass env vars or an env file):

```bash
cd backend
docker build -t spendly-backend:local .
docker run --rm -p 8000:8000 --env-file .env spendly-backend:local
```

Uses **Gunicorn**; worker count via **`WEB_CONCURRENCY`** (default `3`). Production images run **`collectstatic`** at build time (WhiteNoise).

---

## 6. Kubernetes & CI

- **Manifests:** `deploy/kubernetes/` — namespace, Deployment, Service, Ingress example, migrate **Job**, and **`backend-secret.example.yaml`** (copy to `backend-secret.yaml` and apply; the real secret file is gitignored).
- **GitHub Actions:** `.github/workflows/backend-ci.yml` — on changes under `backend/`, runs migrate/check/collectstatic against Postgres, then on **`main`** builds and pushes **`ghcr.io/<lowercase-owner>/spendly-backend`** (`:latest` and `:<sha>`).

---

## 7. Quick checklist (Django + React)

| Step | Action |
|------|--------|
| PostgreSQL | Running; database created |
| Env | `backend/.env` from `backend/.env.example` |
| Backend | `pip install -r requirements.txt` → `migrate` → `runserver 8000` |
| Frontend | `npm install` → `npm run dev` |

---

## 8. Tests

If the repo includes Flask tests:

```bash
source .venv/bin/activate
pytest
```

---

## 9. Troubleshooting

| Issue | What to try |
|-------|-------------|
| `relation "api_..." does not exist` | `cd backend && python manage.py migrate` |
| Database connection errors | Check `DB_*` in `backend/.env` and that Postgres is up |
| React 404/502 on API | Run Django on **8000** with `npm run dev`, or set `VITE_API_BASE` in `frontend/.env` |
| CORS errors | Add your site origin to `CORS_ALLOWED_ORIGINS` in `backend/.env` |

---

## 10. Project layout

```
expense-tracker/
├── .env.example              # Env template (root + shared vars)
├── .gitignore                # Ignores .env, venvs, node_modules, K8s secrets, …
├── requirements.txt          # Optional Flask stack (when app.py exists)
├── backend/
│   ├── .env.example
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── requirements-prod.txt   # + gunicorn (Docker)
│   ├── manage.py
│   ├── spendly/              # Django settings & URLs
│   └── api/                  # Models, views, serializers
├── frontend/
│   ├── .env.example
│   └── src/                  # React app
├── deploy/kubernetes/        # K8s manifests + secret example
└── .github/workflows/        # Backend CI & image push
```
