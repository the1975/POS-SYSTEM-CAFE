from enum import StrEnum


def enum_check(column: str, values: type[StrEnum]) -> str:
    """SQL CHECK: kolom string hanya boleh berisi nilai dari enum.
    Satu sumber kebenaran: tambah nilai di enum, migrasi baru memperbarui CHECK-nya."""
    return f"{column} IN ({', '.join(repr(v.value) for v in values)})"
