"""
Backend: API endpoints para frontend
"""

import json
from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI
from app.db import ensure_tables, get_conn
from psycopg2.extras import RealDictCursor

ensure_tables()

app = FastAPI()

@app.get("/api/readings")
def list_readings(
    timestamp: Optional[str] = None,
    range_seconds: int = 600  # Default to ±5 minutes
):
    with get_conn() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)

        sql = """
            SELECT 
                cr.container_id, 
                cr.timestamp, 
                cr.fill_level, 
                cr.received_at,
                ST_X(c.location::geometry) AS lon,
                ST_Y(c.location::geometry) AS lat
            FROM container_readings cr
            JOIN containers c ON cr.container_id = c.id
        """
        params = []

        if timestamp:
            try:
                ts = datetime.fromisoformat(timestamp)
            except ValueError:
                return {"error": "Invalid timestamp format. Use ISO8601."}

            start_time = ts - timedelta(seconds=range_seconds)
            end_time = ts + timedelta(seconds=range_seconds)

            sql += " WHERE cr.timestamp BETWEEN %s AND %s"
            params += [start_time, end_time]

        sql += " ORDER BY cr.timestamp DESC"

        cur.execute(sql, params)
        return cur.fetchall()

@app.get("/api/zones")
def list_zones():
    with get_conn() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT 
                id, 
                name,
                ST_AsGeoJSON(boundary::geometry) AS geojson
            FROM zones;
        """)
        zones = cur.fetchall()

        # Deserialize GeoJSON string into actual object
        for zone in zones:
            zone["boundary"] = json.loads(zone.pop("geojson"))

        return zones

@app.get("/api/containers")
def list_containers():
    with get_conn() as conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT 
                id,
                node_id,
                zone_id,
                type,
                created_at,
                ST_X(location::geometry) AS lon,
                ST_Y(location::geometry) AS lat
            FROM containers;
        """)
        return cur.fetchall()