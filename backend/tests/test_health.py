from sqlalchemy.exc import OperationalError

from app.db import get_db
from app.main import app


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_ready_when_db_up(client):
    r = client.get("/ready")
    assert r.status_code == 200
    assert r.json() == {"status": "ready", "database": "up"}


def test_ready_returns_503_when_db_down(client):
    class BrokenDB:
        def execute(self, *_):
            raise OperationalError("SELECT 1", {}, Exception("connection refused"))

    app.dependency_overrides[get_db] = lambda: BrokenDB()
    r = client.get("/ready")
    assert r.status_code == 503
    assert r.json()["database"] == "down"
