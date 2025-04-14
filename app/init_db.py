from db import get_connection
from models.user_model import USER_TABLE
from models.pvz_model import PVZ_TABLE
from models.reception_model import RECEPTION_TABLE
from models.product_model import PRODUCT_TABLE

def init_tables():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(USER_TABLE)
            cur.execute(PVZ_TABLE)
            cur.execute(RECEPTION_TABLE)
            cur.execute(PRODUCT_TABLE)
        conn.commit()

if __name__ == "__main__":
    init_tables()
