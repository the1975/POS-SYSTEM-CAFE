"""Konfigurasi aplikasi. Semua nilai bisnis yang bisa berubah (mis. timeout reservasi)
dibaca dari environment, bukan di-hardcode di banyak tempat."""
from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", "../.env"), extra="ignore")

    app_env: str = "development"
    log_level: str = "INFO"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/monster_cafe"
    # Disimpan sebagai string "a,b" agar mudah diisi lewat env var.
    cors_origins: str = "http://localhost:5173"
    reservation_timeout_minutes: int = 7

    @field_validator("reservation_timeout_minutes")
    @classmethod
    def _positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("reservation_timeout_minutes must be > 0")
        return v

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
