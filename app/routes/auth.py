from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from schemas.user_schema import UserCreate, LoginSchema, UserOut
from schemas.token_schema import Token
from services.token_service import create_token
from db import get_connection
import uuid

router = APIRouter()


class DummyLoginRequest(BaseModel):
    role: str


@router.post(
    "/dummyLogin",
    response_model=Token,
    status_code=200,
    summary="Получение тестового токена",
    responses={
     200: {"description": "Успешная авторизация"},
     400: {"description": "Неверный запрос"}
    }
)
def dummy_login(body: DummyLoginRequest):
    if body.role not in ["employee", "moderator"]:
        raise HTTPException(status_code=400, detail="Неверный запрос")
    token = create_token({"role": body.role, "email": f"{body.role}@dummy.com"})
    return {"token": token}


@router.post(
    "/register",
    response_model=UserOut,
    status_code=201,
    summary="Регистрация пользователя",
    responses={
     201: {"description": "Пользователь создан"},
     400: {"description": "Ошибка при создании пользователя"}
    }
)
def register_user(user: UserCreate):
    if user.role not in ["employee", "moderator"]:
        raise HTTPException(status_code=400, detail="Неверный запрос")
    with get_connection() as conn:
        with conn.cursor() as cur:
            user_id = str(uuid.uuid4())
            try:
                cur.execute(
                    "INSERT INTO users (id, email, password, role) VALUES (%s, %s, %s, %s) RETURNING id, email, role",
                    (user_id, user.email, user.password, user.role)
                )
                row = cur.fetchone()
                return {"id": row[0], "email": row[1], "role": row[2]}
            except Exception:
                raise HTTPException(status_code=400, detail="Ошибка при создании пользователя")


@router.post(
    "/login",
    response_model=Token,
    status_code=200,
    summary="Авторизация пользователя",
    responses={
     200: {"description": "Успешная авторизация"},
     401: {"description": "Неверные учетные данные"}
    }
)
def login_user(credentials: LoginSchema):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT email, role FROM users WHERE email = %s AND password = %s",
                (credentials.email, credentials.password)
            )
            user = cur.fetchone()
            if not user:
                raise HTTPException(status_code=401, detail="Неверные учетные данные")
            token = create_token({"email": user[0], "role": user[1]})
            return {"token": token}
