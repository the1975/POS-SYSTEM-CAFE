# Backend — Monster Café

FastAPI + SQLAlchemy 2.x + Alembic + PostgreSQL (modular monolith).

## Jalankan lokal
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp ../.env.example ../.env      # lalu isi DATABASE_URL
uvicorn app.main:app --reload
```
- Liveness: `GET /api/v1/health`
- Readiness (cek DB): `GET /api/v1/health/ready`
- Docs (non-production): `/docs`

## Test & lint
```bash
pytest
ruff check .
```
