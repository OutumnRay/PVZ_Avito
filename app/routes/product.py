from fastapi import Body, APIRouter, Depends, HTTPException
from schemas.product_schema import ProductOut
from services.auth_service import get_current_user
from uuid import uuid4
from db import get_connection
from datetime import datetime


router = APIRouter()


@router.post(
    "",
    response_model=ProductOut,
    status_code=201,
    summary="Добавление товара в текущую приемку (только для сотрудников ПВЗ)",
    responses={
        201: {"description": "Товар добавлен"},
        400: {"description": "Неверный запрос или нет активной приемки"},
        403: {"description": "Доступ запрещен"},
    }
)
def add_product(
    payload: dict = Body(...),
    user=Depends(get_current_user)
):
    if user["role"] != "employee":
        raise HTTPException(status_code=403, detail="Permission denied")

    pvz_id = payload.get("pvzId")
    product_type = payload.get("type")

    if not pvz_id or not product_type:
        raise HTTPException(status_code=400, detail="pvzId и type обязательны")

    if product_type not in ["электроника", "одежда", "обувь"]:
        raise HTTPException(status_code=400, detail="Недопустимый тип товара")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM receptions WHERE pvz_id = %s AND status = 'in_progress' ORDER BY date_time DESC LIMIT 1",
                (pvz_id,)
            )
            reception = cur.fetchone()
            if not reception:
                raise HTTPException(status_code=400, detail="Нет активной приемки")

            product_id = str(uuid4())
            now = datetime.now()
            cur.execute(
                "INSERT INTO products (id, reception_id, date_time, type) VALUES (%s, %s, %s, %s) RETURNING id, date_time, type",
                (product_id, reception[0], now, product_type)
            )
            row = cur.fetchone()
            return {
                "id": row[0],
                "dateTime": row[1],
                "type": row[2],
                "receptionId": reception[0]
            }