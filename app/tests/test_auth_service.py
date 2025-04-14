import pytest
from fastapi import HTTPException
from services.token_service import create_token
from services.auth_service import get_current_user


def test_valid_token():
    token = create_token({"email": "user@test.com", "role": "employee"})
    header = f"Bearer {token}"
    user = get_current_user(authorization=header)
    assert user["email"] == "user@test.com"


def test_invalid_token_format():
    with pytest.raises(HTTPException) as exc_info:
        get_current_user("InvalidTokenFormat")
    assert exc_info.value.status_code == 403


def test_invalid_token_decoding():
    with pytest.raises(HTTPException) as exc_info:
        get_current_user("Bearer invalid.token")
    assert exc_info.value.status_code == 403
