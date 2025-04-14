from fastapi import APIRouter, Depends, HTTPException, Query, Path
from services.auth_service import get_current_user
from schemas.pvz_schema import PVZCreate, PVZOut
from schemas.reception_schema import ReceptionOut
from db import get_connection
from datetime import datetime
import uuid

router = APIRouter()

ALLOWED_CITIES = ["Москва", "Санкт-Петербург", "Казань"]

@router.post(
    "",
    response_model=PVZOut,
    status_code=201,
    summary="Создание ПВЗ (только для модераторов)",
    responses={
        201: {"description": "ПВЗ создан"},
        400: {"description": "Неверный запрос"},
        403: {"description": "Доступ запрещен"},
    }
)
def create_pvz(data: PVZCreate, user=Depends(get_current_user)):
    if user["role"] != "moderator":
        raise HTTPException(status_code=403, detail="Permission denied")

    if data.city not in ALLOWED_CITIES:
        raise HTTPException(status_code=400, detail="Недопустимый город")

    pvz_id = str(uuid.uuid4())
    now = datetime.now()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO pvz (id, registration_date, city) VALUES (%s, %s, %s) RETURNING id, registration_date, city",
                (pvz_id, now, data.city)
            )
            row = cur.fetchone()
            return {"id": row[0], "registrationDate": row[1], "city": row[2]}


@router.get(
    "",
    summary="Получение списка ПВЗ с фильтрацией по дате приемки и пагинацией",
    responses={200: {"description": "Список ПВЗ"}}
)
def list_pvz(
    startDate: str = Query(None),
    endDate: str = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=30),
    user=Depends(get_current_user)
):
    if user["role"] not in ["employee", "moderator"]:
        raise HTTPException(status_code=403, detail="Permission denied")

    offset = (page - 1) * limit

    with get_connection() as conn:
        with conn.cursor() as cur:
            query = """
                SELECT pvz.id, pvz.registration_date, pvz.city,
                       r.id, r.date_time, r.status,
                       p.id, p.date_time, p.type
                FROM pvz
                LEFT JOIN receptions r ON r.pvz_id = pvz.id
                LEFT JOIN products p ON p.reception_id = r.id
            """

            filters = []
            params = []

            if startDate:
                filters.append("r.date_time >= %s")
                params.append(startDate)
            if endDate:
                filters.append("r.date_time <= %s")
                params.append(endDate)

            if filters:
                query += " WHERE " + " AND ".join(filters)

            query += " ORDER BY pvz.registration_date DESC OFFSET %s LIMIT %s"
            params.extend([offset, limit])

            cur.execute(query, params)
            rows = cur.fetchall()

    result = {}
    for row in rows:
        pvz_id = row[0]
        if pvz_id not in result:
            result[pvz_id] = {
                "pvz": {"id": row[0], "registrationDate": row[1], "city": row[2]},
                "receptions": []
            }
        reception_id = row[3]
        if reception_id:
            rec_entry = next((r for r in result[pvz_id]["receptions"] if r["reception"]["id"] == reception_id), None)
            if not rec_entry:
                rec_entry = {
                    "reception": {
                        "id": row[3],
                        "dateTime": row[4],
                        "status": row[5]
                    },
                    "products": []
                }
                result[pvz_id]["receptions"].append(rec_entry)

            product_id = row[6]
            if product_id:
                rec_entry["products"].append({
                    "id": row[6],
                    "dateTime": row[7],
                    "type": row[8],
                    "receptionId": row[3]
                })

    return list(result.values())


@router.post(
    "/{pvz_id}/close_last_reception",
    response_model=ReceptionOut,
    summary="Закрытие последней открытой приемки товаров в рамках ПВЗ",
    responses={
        200: {"description": "Приемка закрыта"},
        400: {"description": "Неверный запрос или приемка уже закрыта"},
        403: {"description": "Доступ запрещен"},
    }
)
def close_last_reception(
    pvz_id: str = Path(..., title="PVZ ID"),
    user=Depends(get_current_user)
):
    if user["role"] not in ["employee", "moderator"]:
        raise HTTPException(status_code=403, detail="Permission denied")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, date_time, status FROM receptions WHERE pvz_id = %s AND status = 'in_progress' ORDER BY date_time DESC LIMIT 1",
                (pvz_id,)
            )
            reception = cur.fetchone()

            if not reception:
                raise HTTPException(status_code=400, detail="Нет открытых приемок для закрытия")

            cur.execute(
                "UPDATE receptions SET status = 'close' WHERE id = %s RETURNING id, date_time, status",
                (reception[0],)
            )
            updated = cur.fetchone()
            return {"id": updated[0], "dateTime": updated[1], "status": updated[2]}


@router.post(
    "/{pvz_id}/delete_last_product",
    summary="Удаление последнего добавленного товара из текущей приемки (только для сотрудников ПВЗ)",
    responses={
        200: {"description": "Товар удален"},
        400: {"description": "Нет активной приемки или нет товаров для удаления"},
        403: {"description": "Доступ запрещен"},
    }
)
def delete_last_product(
    pvz_id: str = Path(..., title="PVZ ID"),
    user=Depends(get_current_user)
):
    if user["role"] != "employee":
        raise HTTPException(status_code=403, detail="Permission denied")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM receptions WHERE pvz_id = %s AND status = 'in_progress' ORDER BY date_time DESC LIMIT 1",
                (pvz_id,)
            )
            reception = cur.fetchone()
            if not reception:
                raise HTTPException(status_code=400, detail="Нет активной приемки")

            reception_id = reception[0]

            cur.execute(
                "SELECT id FROM products WHERE reception_id = %s ORDER BY date_time DESC LIMIT 1",
                (reception_id,)
            )
            product = cur.fetchone()
            if not product:
                raise HTTPException(status_code=400, detail="Нет товаров для удаления")

            cur.execute("DELETE FROM products WHERE id = %s", (product[0],))
            return {"detail": "Товар удален"}
