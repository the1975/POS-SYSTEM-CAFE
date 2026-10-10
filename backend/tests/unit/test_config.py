import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_cors_origin_list_parsing():
    s = Settings(cors_origins="http://a.com, http://b.com ,")
    assert s.cors_origin_list == ["http://a.com", "http://b.com"]


def test_reservation_timeout_default_and_override():
    assert Settings().reservation_timeout_minutes == 7
    assert Settings(reservation_timeout_minutes=10).reservation_timeout_minutes == 10


def test_reservation_timeout_must_be_positive():
    with pytest.raises(ValidationError):
        Settings(reservation_timeout_minutes=0)


def test_production_requires_tracking_token_secret():
    with pytest.raises(ValidationError):
        Settings(app_env="production", tracking_token_secret=None)
    # Dengan rahasia terisi, production boleh jalan.
    assert Settings(app_env="production", tracking_token_secret="x" * 32).is_production


def test_tax_rate_must_be_a_valid_percentage():
    with pytest.raises(ValidationError):
        Settings(tax_rate_percent=150)


def test_production_requires_tracking_token_secret():
    with pytest.raises(ValidationError):
        Settings(app_env="production", tracking_token_secret=None)
    # Dengan rahasia terisi, production boleh jalan.
    assert Settings(app_env="production", tracking_token_secret="x" * 32).is_production


def test_tax_rate_must_be_a_valid_percentage():
    with pytest.raises(ValidationError):
        Settings(tax_rate_percent=150)
