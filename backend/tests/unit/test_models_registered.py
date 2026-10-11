import subprocess
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[2]


def test_app_registers_all_tables_on_its_own():
    """Meniru server asli: proses Python baru yang HANYA meng-import app.main.
    Di test biasa conftest sudah meng-import semua model, jadi bug 'tabel belum terdaftar'
    (FK ke users tidak ketemu) tidak akan terlihat tanpa test terpisah seperti ini."""
    code = (
        "from app.main import app; from app.db.base import Base; "
        "print(len(Base.metadata.tables))"
    )
    result = subprocess.run(
        [sys.executable, "-c", code], cwd=BACKEND, capture_output=True, text=True, timeout=60, check=False
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip().splitlines()[-1] == "18"
