# Spendly API (Django)

PostgreSQL (recommended) or SQLite for local dev.

## Setup

```bash
cd backend
python -m venv .venv && source .venv/bin/activate  # optional
pip install -r requirements.txt
```

Copy **`backend/.env.example`** to **`backend/.env`** and set variables (see table below). For SQLite only:

```bash
export DJANGO_USE_SQLITE=1
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 8000
```

## Environment

| Variable | Description |
|----------|-------------|
| `DJANGO_SECRET_KEY` | Secret key |
| `DJANGO_DEBUG` | `1` or `0` |
| `DJANGO_USE_SQLITE` | Set `1` to use `backend/db.sqlite3` |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | PostgreSQL (omit `DJANGO_USE_SQLITE`) |
| `CORS_ALLOWED_ORIGINS` | Comma-separated, e.g. `http://localhost:5173` |
| `JWT_ACCESS_MINUTES` | Access token lifetime |

API base: `http://127.0.0.1:8000/api/`

## Endpoints (summary)

- `POST /api/register/`, `POST /api/login/`, `POST /api/token/refresh/`
- `GET|PATCH /api/profile/`
- `GET|POST /api/expenses/` — personal expenses (UUID user PK)
- `GET|POST /api/groups/`, `GET /api/groups/<uuid>/`
- `GET|POST /api/groups/<uuid>/expenses/`, `GET|PUT|PATCH|DELETE /api/groups/<uuid>/expenses/<uuid>/`
- `POST /api/groups/<uuid>/invites/` body `{"username":"..."}`
- `GET /api/invitations/pending/`, `POST .../accept/`, `POST .../decline/`
- `GET /api/search/users/?q=`, `GET /api/search/groups/?q=`
- `GET /api/notifications/`, `POST .../mark-all-read/`, `POST .../<id>/mark-read/`
- `GET|POST /api/groups/<uuid>/chat/`
- `GET|POST /api/chat/direct/<user_uuid>/`

Many write endpoints return `{ "success": true, "data": ... }` via `api.responses.ok`.

The legacy **Flask** app in the repo root is unchanged; this backend is separate.
