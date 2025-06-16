import os
import json
from fastapi import FastAPI, Request
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

app = FastAPI()

# --- PostgreSQL Config ---
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

# --- Ensure schema exists (run once) ---
def ensure_tables():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS containers (
                id TEXT PRIMARY KEY,
                type TEXT
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS level_data (
                id SERIAL PRIMARY KEY,
                container_id TEXT REFERENCES containers(id),
                timestamp TIMESTAMP,
                fill_level FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()

ensure_tables()

# --- API: Receive data from edge node ---
@app.post("/api/report")
async def report(payload: dict):
    container_id = payload.get("container_id")
    timestamp = payload.get("timestamp")
    fill_level = payload.get("fill_level")

    if not all([container_id, timestamp, fill_level]):
        return {"status": "error", "detail": "Missing fields"}

    with get_conn() as conn:
        cur = conn.cursor()
        # Ensure container exists
        cur.execute("SELECT id FROM containers WHERE id = %s;", (container_id,))
        if not cur.fetchone():
            cur.execute("INSERT INTO containers (id, type) VALUES (%s, %s);",
                        (container_id, "simulated"))
        
        # Insert level data
        cur.execute("""
            INSERT INTO level_data (container_id, timestamp, fill_level)
            VALUES (%s, %s, %s);
        """, (container_id, timestamp, fill_level))
        conn.commit()

    return {"status": "ok"}

# --- API: Get recent data ---
@app.get("/api/contenedores")
def contenedores():
    with get_conn() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT container_id, timestamp, fill_level, created_at
            FROM level_data
            ORDER BY timestamp DESC
            LIMIT 100;
        """)
        rows = cur.fetchall()
    return rows
