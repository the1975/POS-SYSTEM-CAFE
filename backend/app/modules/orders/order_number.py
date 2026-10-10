"""Nomor order untuk manusia: A001 ... A999, B001 ... Z999, AA001, ...
Dari nomor urut global (SEQUENCE PostgreSQL), jadi UNIK selamanya (aturan: order_number UNIQUE)
tanpa perlu reset harian. Dengan ~150 order/hari, huruf berganti kira-kira tiap 7 hari."""

NUMBERS_PER_LETTER_BLOCK = 999


def _block_letters(index: int) -> str:
    """0 -> A, 25 -> Z, 26 -> AA (seperti kolom Excel)."""
    letters = ""
    n = index + 1
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        letters = chr(65 + remainder) + letters
    return letters


def format_order_number(sequence: int) -> str:
    if sequence < 1:
        raise ValueError("sequence harus >= 1")
    block, offset = divmod(sequence - 1, NUMBERS_PER_LETTER_BLOCK)
    return f"{_block_letters(block)}{offset + 1:03d}"
