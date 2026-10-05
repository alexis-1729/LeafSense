from app.services.password_hasher import hash_password, verify_password


def test_password_hash_verifies_only_matching_password() -> None:
    hashed = hash_password("correct-horse-battery-staple")

    assert hashed != "correct-horse-battery-staple"
    assert verify_password("correct-horse-battery-staple", hashed)
    assert not verify_password("incorrect-password", hashed)
