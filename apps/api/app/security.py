"""Password hashing with Argon2id."""

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from app.validation import normalise_password

# PasswordHasher() uses Argon2id with the library's current default settings.
# Before launch these settings should be checked against OWASP's
# "Password Storage" cheat sheet.
_hasher = PasswordHasher()


def hash_password(password: str) -> str:
    """Return a salted Argon2id hash. The password itself is never stored."""
    return _hasher.hash(normalise_password(password))


def verify_password(password: str, stored_hash: str) -> bool:
    """True if the password matches the stored hash."""
    try:
        return _hasher.verify(stored_hash, normalise_password(password))
    except (VerificationError, InvalidHashError):
        return False
