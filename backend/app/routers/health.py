"""Health endpoints, used by Docker, Kubernetes and load balancers.

/health  (liveness)  "Is the process alive?"       -> if it fails, restart the container
/ready   (readiness) "Can it serve traffic now?"   -> if it fails, stop sending users to it
"""
import logging

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db

router = APIRouter(tags=["health"])
log = logging.getLogger(__name__)


@router.get("/health")
def health():
    s = get_settings()
    return {"status": "ok", "version": s.app_version, "environment": s.environment}


@router.get("/ready")
def ready(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        log.warning("readiness check failed: database unreachable (%s)", type(exc).__name__)
        return JSONResponse(status_code=503, content={"status": "unavailable", "database": "down"})
    return {"status": "ready", "database": "up"}
