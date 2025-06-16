"""
Worker: procesa datos de la base PostgreSQL.
No usa MQTT, ya que los datos llegan vía HTTP a /api/report.
"""

import os
import time
import psycopg2
from psycopg2.extras import RealDictCursor

DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_NAME = os.getenv("POSTGRES_DB", "sced")
DB_USER = os.getenv("POSTGRES_USER", "sced_user")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "securepass")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

def get_conn():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        port=DB_PORT
    )

def process_data():
    """
    Ejemplo: imprimir el promedio de fill_level cada minuto.
    """
    while True:
        with get_conn() as conn:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute("""
                SELECT container_id, AVG(fill_level) as avg_fill
                FROM level_data
                WHERE timestamp >= NOW() - INTERVAL '5 minutes'
                GROUP BY container_id;
            """)
            rows = cur.fetchall()
            print("📊 Promedio últimos 5 min:")
            for row in rows:
                print(f"- {row['container_id']}: {row['avg_fill']:.2f}%")
        time.sleep(60)

if __name__ == "__main__":
    process_data()
