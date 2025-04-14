import psycopg2


def get_connection():
    return psycopg2.connect(
        dbname="pvz_db",
        user="pvz_user",
        password="riop123455",
        host="pvz_db",
        port="5432",
        options="-c client_encoding=UTF8"
    )


def create_tables():
    commands = [
        '''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(50) NOT NULL
        )
        ''',
        '''
        CREATE TABLE IF NOT EXISTS pvz (
            id SERIAL PRIMARY KEY,
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            city VARCHAR(100) NOT NULL CHECK (city IN ('Москва', 'Санкт-Петербург', 'Казань'))
        )
        ''',
        '''
        CREATE TABLE IF NOT EXISTS receptions (
            id SERIAL PRIMARY KEY,
            date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            pvz_id INTEGER NOT NULL,
            status VARCHAR(50) NOT NULL CHECK (status IN ('in_progress', 'close')),
            FOREIGN KEY (pvz_id) REFERENCES pvz (id)
        )
        ''',
        '''
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            type VARCHAR(100) NOT NULL CHECK (type IN ('электроника', 'одежда', 'обувь')),
            reception_id INTEGER NOT NULL,
            FOREIGN KEY (reception_id) REFERENCES receptions (id)
        )
        '''
    ]
    conn = None
    try:
        conn = psycopg2.connect(
            dbname="pvz_db",
            user="pvz_user",
            password="riop123455",
            host="pvz_db",
            port="5432",
            options="-c client_encoding=UTF8"
        )
        cur = conn.cursor()
        for command in commands:
            cur.execute(command)
        cur.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    create_tables()
