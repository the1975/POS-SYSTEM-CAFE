"""Laporan penjualan untuk dashboard admin. Tanggal dibaca dalam zona WIB (UTC+7)."""

from datetime import UTC, date, datetime, time, timedelta, timezone
from decimal import Decimal

from app.modules.analytics.exceptions import InvalidDateRangeError
from app.modules.analytics.repository import AnalyticsRepository
from app.modules.analytics.schema import PeakHourOut, SummaryOut, TopProductOut

# WIB tetap UTC+7 (tanpa DST), jadi tidak perlu database zona waktu.
WIB = timezone(timedelta(hours=7), "WIB")
MAX_RANGE_DAYS = 366


def resolve_range(
    start: date | None, end: date | None, today: date | None = None
) -> tuple[date, date, datetime, datetime]:
    """Default: hari ini. Hanya end diisi = satu hari itu. Hanya start diisi = start s/d hari ini.
    Mengembalikan tanggal dan batas waktu UTC [awal, akhir) untuk query."""
    today = today or datetime.now(WIB).date()
    end = end or today
    start = start or end
    if start > end:
        raise InvalidDateRangeError("Tanggal mulai tidak boleh setelah tanggal akhir.")
    if (end - start).days + 1 > MAX_RANGE_DAYS:
        raise InvalidDateRangeError(f"Rentang tanggal maksimal {MAX_RANGE_DAYS} hari.")
    start_dt = datetime.combine(start, time.min, tzinfo=WIB).astimezone(UTC)
    end_dt = datetime.combine(end + timedelta(days=1), time.min, tzinfo=WIB).astimezone(UTC)
    return start, end, start_dt, end_dt


class AnalyticsService:
    def __init__(self, repo: AnalyticsRepository) -> None:
        self.repo = repo

    def summary(self, start: date | None, end: date | None) -> SummaryOut:
        start, end, start_dt, end_dt = resolve_range(start, end)
        revenue, orders, units = self.repo.summary(start_dt, end_dt)
        average = (revenue / orders).quantize(Decimal("1")) if orders else Decimal(0)
        return SummaryOut(
            start_date=start,
            end_date=end,
            revenue=revenue,
            orders=orders,
            units_sold=units,
            average_order_value=average,
        )

    def top_products(
        self, start: date | None, end: date | None, limit: int
    ) -> list[TopProductOut]:
        _, _, start_dt, end_dt = resolve_range(start, end)
        rows = self.repo.top_products(start_dt, end_dt, limit)
        return [
            TopProductOut(
                product_id=r.product_id,
                product_name=r.product_name,
                units_sold=int(r.units_sold),
                revenue=Decimal(str(r.revenue)),
            )
            for r in rows
        ]

    def peak_hours(self, start: date | None, end: date | None) -> list[PeakHourOut]:
        _, _, start_dt, end_dt = resolve_range(start, end)
        counts = [0] * 24
        for paid_at in self.repo.paid_times(start_dt, end_dt):
            if paid_at.tzinfo is None:  # SQLite mengembalikan waktu tanpa zona (isinya UTC)
                paid_at = paid_at.replace(tzinfo=UTC)
            counts[paid_at.astimezone(WIB).hour] += 1
        # Semua 24 jam selalu ada (jam sepi = 0) supaya grafik tidak bolong.
        return [PeakHourOut(hour=h, orders=counts[h]) for h in range(24)]
