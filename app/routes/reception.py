from fastapi import Body, APIRouter, Depends, HTTPException
from schemas.reception_schema import ReceptionOut
from services.auth_service import get_current_user
from uuid import uuid4
from db import get_connection
from datetime import datetime


router = APIRouter()


@router.post(
    "",
    response_model=ReceptionOut,
    status_code=201,
    summary="Создание новой приемки товаров (только для сотрудников ПВЗ)",
    responses={
        201: {"description": "Приемка создана"},
        400: {"description": "Неверный запрос или есть незакрытая приемка"},
        403: {"description": "Доступ запрещен"},
    }
)
def create_reception(
    payload: dict = Body(...),
    user=Depends(get_current_user)
):
    if user["role"] != "employee":
        raise HTTPException(status_code=403, detail="Permission denied")

    pvz_id = payload.get("pvzId")
    if not pvz_id:
        raise HTTPException(status_code=400, detail="pvzId обязателен")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM receptions WHERE pvz_id = %s AND status = 'in_progress'",
                (pvz_id,)
            )
            if cur.fetchone():
                raise HTTPException(status_code=400, detail="Уже есть открытая приемка")

            rec_id = str(uuid4())
            now = datetime.now()
            cur.execute(
                "INSERT INTO receptions (id, pvz_id, date_time, status) VALUES (%s, %s, %s, %s) RETURNING id, date_time, status",
                (rec_id, pvz_id, now, 'in_progress')
            )
            row = cur.fetchone()
            return {"id": row[0], "dateTime": row[1], "status": row[2]}
