import os
import json
from fastapi import FastAPI
from pydantic import BaseModel
import paho.mqtt.publish as publish
from app.settings import MQTT_BROKER, MQTT_PORT, MQTT_TOPIC
from app.db import ensure_tables, get_conn
from psycopg2.extras import RealDictCursor

ensure_tables()

app = FastAPI()

class ReportPayload(BaseModel):
    node_id: str
    container_id: str
    fill_level: float
    timestamp: str
    created_at: str

# --- API: Receive data from edge node ---
@app.post("/api/report")
async def report(payload: ReportPayload):
    # Ensure node exists or create it with NULL location
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id, ST_AsGeoJSON(location) AS location FROM processor_nodes WHERE id = %s", (payload.node_id,))
            node = cur.fetchone()
            if not node:
                cur.execute("INSERT INTO processor_nodes (id, location) VALUES (%s, NULL)", (payload.node_id,))
                conn.commit()
                node = {"id": payload.node_id, "location": None}

    if "location" not in node or node["location"] is None:
        raise Exception("ERR location")

    mqtt_payload = {
        "node_id": payload.node_id,
        "container_id": payload.container_id,
        "fill_level": payload.fill_level,
        "location": json.loads(node["location"]),
        "timestamp": payload.timestamp,
        "created_at": payload.created_at
    }

    # Publish the message to MQTT
    publish.single(
        MQTT_TOPIC,
        payload=json.dumps(mqtt_payload),
        hostname=MQTT_BROKER,
        port=MQTT_PORT
    )

    return {"status": "queued"}