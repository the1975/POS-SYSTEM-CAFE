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
