"""Perhitungan uang order. Fungsi murni: tanpa database, mudah diuji.
Alur: subtotal -> diskon -> DPP -> pajak -> total (backend yang menghitung, bukan frontend)."""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

WHOLE_RUPIAH = Decimal(1)


@dataclass(frozen=True)
class Totals:
    subtotal: Decimal
    discount_amount: Decimal
    taxable_base: Decimal  # DPP = subtotal - diskon
    tax_amount: Decimal
    total: Decimal


def calculate_totals(subtotal: Decimal, discount: Decimal, tax_rate_percent: Decimal) -> Totals:
    if subtotal < 0 or discount < 0:
        raise ValueError("subtotal dan diskon tidak boleh negatif")
    if discount > subtotal:
        # Total tidak boleh negatif: diskon tidak boleh melebihi subtotal.
        raise ValueError("diskon tidak boleh melebihi subtotal")
    dpp = subtotal - discount
    # Pajak dibulatkan ke rupiah utuh (setengah ke atas).
    tax = (dpp * tax_rate_percent / Decimal(100)).quantize(WHOLE_RUPIAH, ROUND_HALF_UP)
    return Totals(subtotal, discount, dpp, tax, dpp + tax)
