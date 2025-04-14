from fastapi import FastAPI
import uvicorn
from routes.auth import router as auth_router
from routes.pvz import router as pvz_router
from routes.product import router as product_router
from routes.reception import router as reception_router
import os
from init_db import init_tables
from contextlib import asynccontextmanager


def initialize_db():
    if os.getenv("INITIALIZE_DB", "True").lower() == "true":
        init_tables()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Старт работы сервиса...")
    initialize_db()
    yield

    print("Завершение работы сервиса и базы данных...")


app = FastAPI(
    title="Сервис для управления ПВЗ и приемкой товаров",
    lifespan=lifespan
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(pvz_router, prefix="/pvz", tags=["pvz"])
app.include_router(product_router, prefix="/products", tags=["products"])
app.include_router(reception_router, prefix="/receptions", tags=["reception"])


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
