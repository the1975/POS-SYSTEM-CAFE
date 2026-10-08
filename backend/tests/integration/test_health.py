
from app.db.dependencies import get_db


def test_liveness_ok(client):
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_readiness_ok_when_db_reachable(client):
    class FakeDB:
        def execute(self, *_):
            return 1

    client.app.dependency_overrides[get_db] = lambda: FakeDB()
    r = client.get("/api/v1/health/ready")
    assert r.status_code == 200
    assert r.json() == {"status": "ready"}


def test_readiness_503_without_leaking_details(client):
    class BrokenDB:
        def execute(self, *_):
            raise RuntimeError("password=supersecret host=10.0.0.5")

    client.app.dependency_overrides[get_db] = lambda: BrokenDB()
    r = client.get("/api/v1/health/ready")
    assert r.status_code == 503
    assert "supersecret" not in r.text
    assert r.json()["error"]["code"] == "HTTP_ERROR"


def test_cors_allows_configured_origin(client):
    r = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert r.headers.get("access-control-allow-origin") == "http://localhost:5173"
