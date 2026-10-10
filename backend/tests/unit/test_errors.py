from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.core.exceptions import ConflictError, register_exception_handlers


def _app() -> TestClient:
    app = FastAPI()
    register_exception_handlers(app)

    class Item(BaseModel):
        qty: int

    @app.post("/validate")
    def validate(item: Item):
        return item

    @app.get("/conflict")
    def conflict():
        raise ConflictError("Stok tidak cukup.")

    @app.get("/boom")
    def boom():
        raise RuntimeError("SELECT * FROM secret_table")

    return TestClient(app, raise_server_exceptions=False)


def test_validation_error_shape():
    r = _app().post("/validate", json={"qty": "abc"})
    assert r.status_code == 422
    body = r.json()["error"]
    assert body["code"] == "VALIDATION_ERROR"
    assert body["details"][0]["field"] == "qty"


def test_app_error_shape():
    r = _app().get("/conflict")
    assert r.status_code == 409
    assert r.json()["success"] is False
    assert r.json()["error"] == {
        "code": "CONFLICT",
        "message": "Stok tidak cukup.",
        "details": None,
    }


def test_unhandled_error_is_safe():
    r = _app().get("/boom")
    assert r.status_code == 500
    assert "secret_table" not in r.text
    assert r.json()["error"]["code"] == "INTERNAL_ERROR"
