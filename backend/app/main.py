"""NotesHub API entry point. Run with:  uvicorn app.main:app --reload"""
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import health, notes

settings = get_settings()

# Logs go to stdout. In Docker/Kubernetes, the platform collects stdout (later: into Loki).
logging.basicConfig(
    level=settings.log_level.upper(),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger("noteshub")

@asynccontextmanager
async def lifespan(_app: FastAPI):
    log.info("%s v%s starting (environment=%s)", settings.app_name, settings.app_version, settings.environment)
    yield
    log.info("%s shutting down", settings.app_name)


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

# CORS: allow the frontend (a different address/port) to call this API from the browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type"],
)


@app.middleware("http")
async def access_log(request: Request, call_next):
    """Log every request with its status and duration — basic observability."""
    start = time.perf_counter()
    response = await call_next(request)
    ms = (time.perf_counter() - start) * 1000
    log.info("%s %s -> %s (%.1f ms)", request.method, request.url.path, response.status_code, ms)
    return response


app.include_router(health.router)
app.include_router(notes.router)
