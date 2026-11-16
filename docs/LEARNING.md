# NotesHub — My DevOps Learning Journal

A record of every step: **what** we did, **why**, the **commands**, and **interview questions**.

**Project:** NotesHub, a simple notes app (FastAPI + PostgreSQL + HTML), used to learn the full DevOps lifecycle.
**Target cloud:** AWS (EKS, ECR, RDS). We practise locally first to keep costs low.

```
[0] Setup ✅ ─► [1] Build app (backend ✅, frontend next) ─► [2] Docker ─► [3] CI ─► [4] Kubernetes ─► [5] AWS + Terraform ─► [6] CD ─► [7] Monitoring
```

---

## What is a DevOps engineer?

- **Developers (Dev)** write code. **Operations (Ops)** run it on servers.
- A **DevOps engineer** builds the automatic, safe, repeatable "road" from the developer's laptop to the customer.

| Area | Simple meaning | Tools |
|---|---|---|
| Containers | Package the app so it runs the same everywhere | Docker |
| CI | Test and build every code change automatically | GitHub Actions, Jenkins |
| CD | Deploy approved code automatically | GitHub Actions, ArgoCD |
| Infrastructure as Code | Create servers/networks/DBs by writing code | Terraform |
| Orchestration | Run, heal and scale many containers | Kubernetes |
| Cloud | Rent infrastructure | AWS, Azure, GCP |
| Monitoring & logging | Know what broke and why | Prometheus, Grafana, Loki |
| Security | Scan images, protect secrets, limit access | Trivy, IAM, Secrets Manager |

> **One line:** Developers build the app; DevOps makes sure it can be tested, shipped, run, scaled and fixed automatically.

---

## Step 0 — Environment setup ✅ (2026-11-16)

### What we did
| Action | Why | Job term |
|---|---|---|
| Chose stack: FastAPI, PostgreSQL, GitHub Actions, AWS | Every project starts with tech decisions | Architecture decision |
| Checked Windows version, RAM, virtualization, WSL 2 | Tools have system requirements | Environment assessment |
| Checked which Docker versions support Windows 10 | Software drops support for old OS versions | Compatibility check |
| Installed Python 3.15 + Docker Desktop 4.99 | Needed to build and run the app | Dev environment setup |
| Fixed `python` "not found" by adding it to PATH | Windows didn't know where Python was | Troubleshooting |
| Checked all Python packages support 3.15 | New language versions can break packages | Dependency check |
| Estimated AWS EKS cost (~$150/month if left on) | Cloud bills can surprise you | Cost awareness (FinOps) |

### Why Docker?
**Problem:** "It works on my machine!" Different Python versions, libraries and OS between laptop and server break apps.
**Solution:** Docker packages the app **plus everything it needs** into an **image** that runs identically everywhere.
Analogy: a **shipping container**, one standard box that fits every ship, truck and crane.

| Term | Meaning |
|---|---|
| **Image** | Read-only package: app + runtime + libraries (the recipe / frozen meal) |
| **Container** | A running copy of an image |
| **Dockerfile** | Instructions to build an image |
| **Registry** | Online store for images (Docker Hub, AWS ECR, GHCR) |
| **Docker Compose** | Run several containers together (app + database) |
| **Volume** | Storage that survives when a container is deleted |

### What `docker run hello-world` did
1. Looked for the `hello-world` image locally → not found
2. **Pulled** it from Docker Hub (a registry)
3. Created a **container** from the image
4. The container ran and printed "Hello from Docker!"
5. The container was removed (`--rm`)

This proves the full chain works: engine running, internet access, pull + run.

### Commands learned
```powershell
python --version            # check Python
python -m pip --version     # check pip (Python package installer)
docker --version            # check Docker CLI
docker compose version      # check Docker Compose
docker run --rm hello-world # end-to-end Docker test
```

### Interview questions
1. **What is DevOps?** A culture and set of practices that join development and operations to deliver software faster and more reliably through automation, CI/CD, IaC and monitoring.
2. **Container vs virtual machine?** A VM includes a full operating system (heavy, slow to start). A container shares the host's kernel and only packages the app and its dependencies (light, starts in seconds).
3. **Image vs container?** An image is the read-only template; a container is a running instance of it. One image can run as many containers.
4. **What is a registry?** A storage service for images, e.g. Docker Hub, AWS ECR, GitHub Container Registry.

---

## Step 1b — Backend API ✅ (2026-11-16)

### What we built
A **REST API** with FastAPI that stores notes in **PostgreSQL** (running in Docker).

| File | What it does | DevOps reason |
|---|---|---|
| `docker-compose.yml` | Runs PostgreSQL in a container with a **volume** and a **healthcheck** | No manual DB install; data survives restarts |
| `app/config.py` | Reads settings from **environment variables** / `.env` | Same code runs in dev, staging, prod; only config changes (**12-factor app**) |
| `.env.example` | Template of settings (no real secrets) | `.env` holds secrets and is **git-ignored** |
| `app/db.py` | DB connection with `pool_pre_ping` + 3s `connect_timeout` | Survives DB restarts; fails fast instead of hanging |
| `app/models.py` | Tables: `notes`, `tags`, `note_tags` | Data design |
| `app/schemas.py` | Validates input (title 1–200 chars, max 10 tags, …) | Bad data → clear `422` error, not a crash |
| `app/routers/notes.py` | CRUD + search + tag filter | The app's features |
| `app/routers/health.py` | `/health` and `/ready` | Used by Docker, Kubernetes and load balancers |
| `app/main.py` | Logging every request (method, path, status, time) | **Observability**: logs go to stdout, collected later by Loki |
| `alembic/` | **Database migrations** | DB changes are versioned code, applied the same way everywhere |
| `tests/` | 12 automated tests (pytest) | CI will run these on every change |
| `requirements*.txt` | **Pinned** package versions | **Reproducible builds**: same versions every time |
| `.gitignore` | Files git must never save (`.venv`, `.env`) | Never leak secrets into git |

### Key concepts
**REST API / CRUD** — Create (`POST`), Read (`GET`), Update (`PATCH`), Delete (`DELETE`). Status codes: `200` OK, `201` created, `204` deleted, `404` not found, `422` invalid input, `503` not ready.

**Liveness vs readiness** (very common interview question)
| | `/health` (liveness) | `/ready` (readiness) |
|---|---|---|
| Question | Is the process alive? | Can it serve users right now? |
| Checks | Nothing external | Database connection |
| If it fails, Kubernetes… | **restarts** the container | **stops sending traffic** to it (no restart) |
| Why separate? | If the DB is down, restarting the app won't fix it, so liveness must NOT check the DB |

**Database migrations (Alembic)** — Never change production tables by hand. Each change is a numbered script (`0001_...py`) with `upgrade()` and `downgrade()`. `alembic upgrade head` brings any DB to the latest version. The `alembic_version` table remembers which version a DB is on. Later, CI/CD runs migrations automatically before deploying.

**Virtual environment (`.venv`)** — An isolated folder of Python packages for this project only, so projects don't conflict. (Docker does the same thing at a bigger scale.)

**Linting (ruff)** — Automatic code-style and bug checks. Tests check *behaviour*; linting checks *code quality*. Both run in CI.

### Bugs we found by testing failure cases
1. **`/ready` hung 30+ seconds when the DB was down** → added a 3s `connect_timeout`. Now returns `503` in 3s.
   *Lesson:* health checks must be fast; Kubernetes probes time out after a few seconds.
2. **~1 second per request** → `localhost` on Windows tries IPv6 first. Using `127.0.0.1` dropped it to ~35 ms.
   *Lesson:* always test the "unhappy path" (DB down, slow network) not only the happy path.

### Commands learned
```powershell
docker compose up -d                 # start services in background (-d = detached)
docker compose ps                    # list running services
docker compose logs db               # see a service's logs
docker compose stop                  # stop, keep data
docker compose down -v               # remove containers AND volumes (data!)
docker exec noteshub-db psql -U noteshub -d noteshub -c '\dt'   # run a command inside a container
docker inspect -f '{{.State.Health.Status}}' noteshub-db         # healthcheck status

python -m venv .venv                 # create virtual environment
.\.venv\Scripts\Activate.ps1         # activate it
pip install -r requirements-dev.txt  # install pinned packages

alembic upgrade head                 # apply all migrations
alembic current                      # which version is the DB on?
alembic check                        # do the models match the migrations?

uvicorn app.main:app --reload        # run the API (auto-reload on code change)
pytest                               # run tests
ruff check .                         # lint
```

### Interview questions
1. **Liveness vs readiness probe?** See the table above. Liveness failing → restart. Readiness failing → remove from load balancer.
2. **Why shouldn't the liveness probe check the database?** If the DB goes down, every app pod would be restarted in a loop, which doesn't fix the DB and makes recovery harder.
3. **What is a 12-factor app?** Principles for cloud apps. E.g. config in environment variables, logs to stdout, stateless processes, backing services (DB) attached by URL.
4. **How do you manage database schema changes in CI/CD?** Versioned migrations (Alembic/Flyway/Liquibase) stored in git, run automatically in the pipeline before the new app version starts; written to be backward-compatible so old and new app versions both work during rollout.
5. **Why pin dependency versions?** Reproducible builds; an unexpected new version can't break production.
6. **Why must `.env` never be committed?** It contains secrets. Anyone with repo access (or a leaked repo) gets your passwords. Use `.env.example` for templates and a secret manager in production.
7. **What is a Docker volume and why use one for a database?** Storage outside the container's lifecycle; deleting/recreating the container keeps the data.

---
