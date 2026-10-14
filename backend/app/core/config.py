"""Konfigurasi aplikasi. Semua nilai bisnis yang bisa berubah (mis. timeout reservasi)
dibaca dari environment, bukan di-hardcode di banyak tempat."""

from decimal import Decimal
from functools import lru_cache

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", "../.env"), extra="ignore")

    app_env: str = "development"
    log_level: str = "INFO"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/monster_cafe"
    # Disimpan sebagai string "a,b" agar mudah diisi lewat env var.
    cors_origins: str = "http://localhost:5173"
    reservation_timeout_minutes: int = 7
    # Tarif pajak (%) pada order. Nilai kerja sementara; sesuaikan dengan aturan pajak daerah
    # dan konfirmasi ke akuntan sebelum dipakai di produksi.
    tax_rate_percent: Decimal = Field(default=Decimal(10), ge=0, le=100)
    max_quantity_per_item: int = Field(default=20, ge=1, le=999)
    # Kunci rahasia untuk token tracking order. WAJIB di production.
    tracking_token_secret: SecretStr | None = None
    # Rahasia penandatangan token login staff (JWT). WAJIB di production; isi acak panjang.
    jwt_secret: SecretStr | None = None
    access_token_minutes: int = Field(default=60, ge=1, le=1440)
    # Hanya dipakai skrip seed untuk membuat admin awal. Isi di .env, jangan di kode.
    seed_admin_email: str | None = None
    seed_admin_password: SecretStr | None = None

    @field_validator("reservation_timeout_minutes")
    @classmethod
    def _positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("reservation_timeout_minutes must be > 0")
        return v

    @model_validator(mode="after")
    def _secret_required_in_production(self):
        if self.is_production and self.tracking_token_secret is None:
            raise ValueError("TRACKING_TOKEN_SECRET wajib diisi di production")
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
