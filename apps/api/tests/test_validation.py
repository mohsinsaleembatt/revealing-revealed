import pytest

from app.security import hash_password, verify_password
from app.validation import validate_display_name, validate_password


def test_short_password_is_rejected():
    with pytest.raises(ValueError, match="at least 12"):
        validate_password("short")


def test_common_password_is_rejected():
    with pytest.raises(ValueError, match="too easy"):
        # same as a listed one, ignoring case
        validate_password("Password1234")


def test_one_repeated_character_is_rejected():
    with pytest.raises(ValueError, match="too easy"):
        validate_password("aaaaaaaaaaaaaa")


def test_overlong_password_is_rejected():
    with pytest.raises(ValueError, match="at most 128"):
        validate_password("a1" * 65)


def test_good_passphrase_is_accepted_without_character_rules():
    assert validate_password(
        "correct horse battery staple") == "correct horse battery staple"


def test_arabic_display_name_is_accepted():
    assert validate_display_name("عائشة") == "عائشة"


def test_display_name_spaces_are_tidied():
    assert validate_display_name("  Amina   Khan ") == "Amina Khan"


def test_display_name_with_symbols_is_rejected():
    with pytest.raises(ValueError, match="letters"):
        validate_display_name("<script>")


def test_display_name_too_short_is_rejected():
    with pytest.raises(ValueError, match="2 to 50"):
        validate_display_name("A")


def test_hash_is_argon2id_and_verifies():
    stored = hash_password("correct horse battery staple")
    assert stored.startswith("$argon2id$")
    assert verify_password("correct horse battery staple", stored)
    assert not verify_password("wrong password entirely", stored)


def test_same_password_gives_different_hashes():
    first = hash_password("correct horse battery staple")
    second = hash_password("correct horse battery staple")
    assert first != second  # because each hash has its own random salt
