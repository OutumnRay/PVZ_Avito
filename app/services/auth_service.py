from fastapi import HTTPException, Header
from services.token_service import decode_token


def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=403, detail="Invalid token format")

    token = authorization.split(" ")[1]

    try:
        payload = decode_token(token)
        return payload
    except Exception as e:
        raise HTTPException(status_code=403, detail=f"Token validation error: {str(e)}")
