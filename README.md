# Spendly — Expense Tracker

This repository contains **Spendly**, an expense tracker with personal expenses, groups, splits, notifications, and chat.

There are **two ways** to run the project:

| Stack | What it is | Typical URL |
|-------|------------|-------------|
| **Flask** (root) | Classic server-rendered app (`app.py`, Jinja templates, PostgreSQL) | http://127.0.0.1:5001 |
| **Django + React** | REST API (`backend/`) + SPA (`frontend/`) | API: http://127.0.0.1:8000 · UI: http://localhost:5173 |

They use **different code and databases tables** for users. Pick one stack for day-to-day use, or run both if you maintain two databases.

---

## Prerequisites

- **Python 3.11+** (3.12 recommended)
- **PostgreSQL** running locally (or reachable over the network)
- **Node.js 18+** and **npm** (only for the React frontend)

Optional: `git` to clone the repo.

---

## 1. Clone and environment file

```bash
git clone <your-repo-url> expense-tracker
cd expense-tracker
```

Copy the template and fill in secrets (see comments inside the file for what each token is):

```bash
cp .env.example .env
# Django API also needs backend/.env (same values are fine):
cp .env.example backend/.env
# or: cd backend && ln -sf ../.env .env
```

- **Flask** — run from the repo root so **`.env`** is loaded next to `app.py` (see `.env.example`).
- **Django** — reads **`backend/.env`** (see `backend/spendly/settings.py`).
- **React** — **`frontend/.env`** from **`frontend/.env.example`** (`VITE_API_BASE` only; no secrets).

**Credentials you provide:** `FLASK_SECRET_KEY`, `DJANGO_SECRET_KEY`, and PostgreSQL **`DB_*`** (you choose the DB user/password). **GitHub Actions** uses the built-in **`GITHUB_TOKEN`** to push the Docker image to GHCR — nothing to add to `.env`. **Kubernetes** should use the same variable *names* as in `.env.example`, stored in a Secret (see `deploy/kubernetes/backend-secret.example.yaml`).

Create the database in PostgreSQL before starting apps, for example:

```bash
createdb spendly
# or in psql: CREATE DATABASE spendly;
```

**Note:** If your database name contains spaces, quote it in PostgreSQL and set `DB_NAME` exactly as created.

---

## 2. Run the Flask app (classic UI)

```bash
cd expense-tracker
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -c "from database import init_db; init_db()"   # creates/updates tables
python app.py
```

Open **http://127.0.0.1:5001** — register, log in, add expenses, groups, etc.

---

## 3. Run the Django API + React frontend

### 3a. Backend (Django)

```bash
cd expense-tracker/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Ensure **`backend/.env`** exists with `DB_*` set (see section 1).

```bash
cd expense-tracker/backend
python manage.py migrate
python manage.py runserver 8000
```

API base: **http://127.0.0.1:8000/api/**

Optional admin user:

```bash
python manage.py createsuperuser
```

Then open **http://127.0.0.1:8000/admin/**.

### 3b. Frontend (React + Vite)

In a **second terminal**:

```bash
cd expense-tracker/frontend
npm install
npm run dev
```

Open **http://localhost:5173** — the dev server proxies `/api` to `http://127.0.0.1:8000`, so keep Django running on port **8000**.

Register a **new account** in the React app (Django has its own user table, separate from Flask).

---

## 4. Quick checklist

| Step | Flask | Django + React |
|------|--------|----------------|
| PostgreSQL running | Yes | Yes |
| `.env` with `DB_*` | Root `.env` | `backend/.env` (or symlink to root) |
| Install deps | `pip install -r requirements.txt` | `backend`: pip · `frontend`: npm |
| Init DB | `init_db()` via Python | `python manage.py migrate` |
| Start | `python app.py` | `runserver 8000` + `npm run dev` |

---

## 5. Tests (Flask)

```bash
source .venv/bin/activate
pytest
```

---

## 6. Troubleshooting

- **`relation "api_..." does not exist` (Django)**  
  Run migrations: `cd backend && python manage.py migrate`.

- **`could not connect to server` / database errors**  
  Check PostgreSQL is running and `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` in `.env`.

- **React calls API but gets 404/502**  
  Start Django on **port 8000** and use `npm run dev` (Vite proxy). Or set `VITE_API_BASE=http://127.0.0.1:8000/api` in `frontend/.env`.

- **CORS errors** (if you call the API from another origin)  
  Add your origin to `CORS_ALLOWED_ORIGINS` in `.env`.

---

## 7. Project layout (short)

```
expense-tracker/
├── app.py                 # Flask entry
├── database/              # Flask DB helpers (PostgreSQL)
├── templates/             # Flask HTML
├── static/                # Flask CSS/JS
├── backend/               # Django project + REST API
│   ├── manage.py
│   ├── spendly/           # settings, urls
│   └── api/               # models, views, serializers
├── frontend/              # Vite + React SPA
└── README.md              # this file
```

More API detail: **`backend/README.md`**.
