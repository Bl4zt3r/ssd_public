import time
import psycopg2
from app.settings import DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT

def get_conn(retires=5):
    attempt = 1
    while attempt < retires:
        try:
            return psycopg2.connect(
                host=DB_HOST,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASS,
                port=DB_PORT
            )
        except:
            print(f"Failed to connect to DB ({attempt}/{retires})")
        attempt += 1
        time.sleep(5)

# --- Load and execute SQL from file ---
def ensure_tables(sql_path="schema.sql"):
    with open(sql_path, 'r') as f:
        schema_sql = f.read()

    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute(schema_sql)
        conn.commit()
