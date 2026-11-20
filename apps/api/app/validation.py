"""Validation rules for account data. Pure functions: no database, no web."""

import unicodedata

MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_LENGTH = 128  # generous: long passphrases are welcome
MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 50

# A very small sample of well-known weak passwords of 12 or more characters.
# This is only a start. Before launch it should be replaced by a proper
# breached-password check.
COMMON_PASSWORDS = frozenset(
    {
        "password1234",
        "passwordpassword",
        "123456789012",
        "1234567890123",
        "qwertyuiopas",
        "qwertyuiop12",
        "iloveyou1234",
        "welcome12345",
        "letmein12345",
        "administrator",
        "changeme1234",
        "abcdefghijkl",
    }
)


def normalise_password(password: str) -> str:
    """Put a password in a standard Unicode form (NFKC), as NIST SP 800-63B advises,
    so the same typed password always gives the same hash."""
    return unicodedata.normalize("NFKC", password)


def validate_password(password: str) -> str:
    """Return the normalised password, or raise ValueError with a friendly message.

    There are deliberately no rules such as "must contain a digit": current
    NIST guidance recommends length and a blocklist instead.
    """
    password = normalise_password(password)

    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Use at least {MIN_PASSWORD_LENGTH} characters.")
    if len(password) > MAX_PASSWORD_LENGTH:
        raise ValueError(f"Use at most {MAX_PASSWORD_LENGTH} characters.")
    if password.lower() in COMMON_PASSWORDS or len(set(password)) == 1:
        raise ValueError("This password is too easy to guess. Choose another.")
    return password


def validate_display_name(name: str) -> str:
    """Return the cleaned name, or raise ValueError with a friendly message.

    Any script is allowed (so Arabic and Urdu names work): letters, combining
    marks, spaces, hyphens and apostrophes.
    """
    name = unicodedata.normalize("NFC", " ".join(name.split()))  # tidy spaces

    if not MIN_NAME_LENGTH <= len(name) <= MAX_NAME_LENGTH:
        raise ValueError(
            f"Your name must be {MIN_NAME_LENGTH} to {MAX_NAME_LENGTH} characters."
        )
    allowed_extra = " -'\u2019"
    for character in name:
        category = unicodedata.category(character)[0]  # "L" letter, "M" mark
        if category not in ("L", "M") and character not in allowed_extra:
            raise ValueError(
                "Use letters, spaces, hyphens and apostrophes only.")
    if not any(character.isalpha() for character in name):
        raise ValueError("Your name must contain letters.")
    return name
