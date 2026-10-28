import pytest

from db.auth import (
    hash_password,
    hash_token,
    is_valid_password,
    new_session_token,
    verify_password,
)


@pytest.mark.parametrize(
    "password",
    ["correct horse", "12345678", "pässwörd-ünïcode", "x" * 72],
)
def test_hash_is_not_plaintext_and_verifies(password):
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)


@pytest.mark.parametrize(
    "attempt",
    ["wrong password", "Correct horse", "correct horse ", ""],
)
def test_wrong_password_fails(attempt):
    assert not verify_password(attempt, hash_password("correct horse"))


def test_same_password_gets_different_salts():
    assert hash_password("correct horse") != hash_password("correct horse")


@pytest.mark.parametrize("bad_hash", ["not-a-bcrypt-hash", "", "$2b$12$tooshort"])
def test_malformed_hash_fails_instead_of_raising(bad_hash):
    assert not verify_password("correct horse", bad_hash)


@pytest.mark.parametrize(
    "password, expected",
    [
        ("12345678", True),  # exactly the minimum length
        ("x" * 72, True),  # exactly bcrypt's byte limit
        ("é" * 36, True),  # 72 bytes in 36 characters
        ("short", False),
        ("1234567", False),  # one under the minimum
        ("", False),
        ("x" * 73, False),  # one over the byte limit
        ("é" * 37, False),  # 74 bytes in 37 characters
        (None, False),
        (12345678, False),
    ],
)
def test_password_rules(password, expected):
    assert is_valid_password(password) is expected


def test_tokens_are_unique():
    assert new_session_token() != new_session_token()


@pytest.mark.parametrize("token", ["abc", "", new_session_token()])
def test_token_hash_is_stable_and_not_the_token(token):
    assert hash_token(token) == hash_token(token)
    assert len(hash_token(token)) == 64
    assert hash_token(token) != token
