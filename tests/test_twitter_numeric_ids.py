"""X sends snowflake ids as strings on most endpoints and as numbers on a few.

`latest_followers` and `latest_following` return `id` as a JSON number, which the
`id: str` annotation rejected — every call to either endpoint raised
ValidationError before any of the data reached the caller.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from scrapebadger.twitter.models import User


def _user(**overrides):
    payload = {"id": "1862247728845312001", "username": "nasa", "name": "NASA"}
    payload.update(overrides)
    return User(**payload)


def test_string_id_is_unchanged():
    assert _user().id == "1862247728845312001"


def test_numeric_id_is_accepted_and_normalised():
    """The bug: a bare JSON number used to fail validation outright."""
    user = _user(id=1862247728845312001)
    assert user.id == "1862247728845312001"
    assert isinstance(user.id, str)


def test_numeric_id_keeps_full_precision():
    """Snowflakes exceed 2^53, so a float round-trip would corrupt them."""
    assert _user(id=2054998853900775424).id == "2054998853900775424"


@pytest.mark.parametrize("bad", [{"nested": 1}, ["list"]])
def test_structural_change_still_fails(bad):
    """Coercion is for numbers only — a real shape change must still be loud."""
    with pytest.raises(ValidationError):
        _user(id=bad)
