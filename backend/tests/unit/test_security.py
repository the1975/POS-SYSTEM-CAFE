from app.core.security import hash_password, verify_password


def test_hash_is_not_plaintext_and_verifies():
    h = hash_password("kata-sandi-kuat-123")
    assert h != "kata-sandi-kuat-123"
    assert h.startswith("$argon2")
    assert verify_password("kata-sandi-kuat-123", h)


def test_wrong_or_malformed_hash_rejected():
    h = hash_password("kata-sandi-kuat-123")
    assert not verify_password("salah", h)
    assert not verify_password("apa-saja", "bukan-hash-yang-valid")


def test_same_password_gets_different_salt():
    assert hash_password("sama-sama-123") != hash_password("sama-sama-123")
