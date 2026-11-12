"""Password hashing and session token helpers (no database access)"""

import hashlib
import re
import secrets

import bcrypt

_BCRYPT_HASH = re.compile(r"\$2[abxy]\$\d{2}\$[./A-Za-z0-9]{53}")

MIN_PASSWORD_LENGTH = 8
# bcrypt only looks at the first 72 bytes of a password
MAX_PASSWORD_BYTES = 72


def is_valid_password(password: str) -> bool:
    """A password must be 8+ characters and at most 72 bytes (bcrypt's limit)"""
    return (
        isinstance(password, str)
        and len(password) >= MIN_PASSWORD_LENGTH
        and len(password.encode("utf-8")) <= MAX_PASSWORD_BYTES
    )


def hash_password(password: str) -> str:
    """Returns a salted bcrypt hash of the password"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Checks a password against its stored bcrypt hash"""
    # bcrypt panics (not raises) on a truncated hash, so check the format first
    if not _BCRYPT_HASH.fullmatch(password_hash):
        return False
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        # Over-long password
        return False


def new_session_token() -> str:
    """Returns a random token to hand to the client after login"""
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """Hashes a session token for storage; the raw token is never stored"""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
