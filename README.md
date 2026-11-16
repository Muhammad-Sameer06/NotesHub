# NotesHub

A simple notes app (FastAPI + PostgreSQL) used to practise the full DevOps lifecycle.
Learning notes: [docs/LEARNING.md](docs/LEARNING.md)

## Project layout
```
NotesHub/
├── docker-compose.yml      # local PostgreSQL (app containers added in Step 2)
├── docs/LEARNING.md        # learning journal
└── backend/
    ├── app/                # FastAPI application
    │   ├── main.py         # app entry point, logging, CORS
    │   ├── config.py       # settings from environment variables
    │   ├── db.py           # database connection
    │   ├── models.py       # database tables
    │   ├── schemas.py      # API input/output validation
    │   └── routers/        # endpoints: health.py, notes.py
    ├── alembic/            # database migrations
    ├── tests/              # pytest tests
    ├── requirements.txt    # runtime packages (pinned)
    └── requirements-dev.txt# + test/lint tools
```

## Run locally (Windows PowerShell)
Requires Python 3.12+ and Docker Desktop (running).

```powershell
cd E:\NotesHub
docker compose up -d                      # 1. start PostgreSQL

cd backend
python -m venv .venv                      # 2. one-time: create virtual environment
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
Copy-Item .env.example .env               #    one-time: local settings

alembic upgrade head                      # 3. create/upgrade database tables
uvicorn app.main:app --reload             # 4. run the API
```
Open **http://127.0.0.1:8000/docs** for interactive API docs.

## API
| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness: process is alive |
| GET | `/ready` | Readiness: database reachable (503 if not) |
| GET | `/api/notes?search=&tag=&limit=&offset=` | List / search / filter notes |
| POST | `/api/notes` | Create `{"title", "content", "tags": []}` |
| GET | `/api/notes/{id}` | Get one note |
| PATCH | `/api/notes/{id}` | Update some fields |
| DELETE | `/api/notes/{id}` | Delete |

## Quality checks
```powershell
cd backend
ruff check .        # lint
pytest              # tests
```

## Stop
```powershell
docker compose stop      # stop DB, keep data
docker compose down -v   # remove DB AND its data
```
