from services.token_service import create_token, decode_token


def test_create_and_decode_token():
    data = {"email": "test@example.com", "role": "moderator"}
    token = create_token(data)
    decoded = decode_token(token)
    assert decoded["email"] == data["email"]
    assert decoded["role"] == data["role"]
