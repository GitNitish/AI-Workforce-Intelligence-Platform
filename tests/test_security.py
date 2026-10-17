
from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.core.config import settings
from app.core.security import (
    ALGORITHM,
    create_access_token,
    decode_access_token,
)


def test_create_access_token_contains_user_id():
    token = create_access_token("test-user-001")

    payload = decode_access_token(token)

    assert payload["sub"] == "test-user-001"
    assert "exp" in payload


def test_create_access_token_has_expiration():
    token = create_access_token("test-user-002")

    payload = decode_access_token(token)
    expires_at = datetime.fromtimestamp(
        payload["exp"],
        tz=timezone.utc,
    )

    now = datetime.now(timezone.utc)

    assert expires_at > now
    assert expires_at <= now + timedelta(minutes=31)


def test_decode_access_token_rejects_invalid_token():
    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token("not-a-valid-jwt")


def test_decode_access_token_rejects_token_signed_with_wrong_key():
    token = jwt.encode(
        {
            "sub": "test-user-003",
            "exp": datetime.now(timezone.utc)
            + timedelta(minutes=5),
        },
        "a-different-test-key-that-is-long-enough",
        algorithm=ALGORITHM,
    )

    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(token)


def test_configured_secret_key_is_at_least_32_bytes():
    assert len(settings.secret_key.encode("utf-8")) >= 32
