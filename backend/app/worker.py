"""
Worker: procesa datos recibidos por MQTT y los guarda en PostgreSQL/PostGIS
"""

import signal
import sys
import time
import json
import paho.mqtt.client as mqtt
from datetime import datetime
from app.settings import MQTT_BROKER, MQTT_PORT, MQTT_TOPIC
from app.db import ensure_tables, get_conn

ensure_tables()

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
should_exit = False

def ensure_zone_and_node(cur, zone_id: str | None, node_id: str, location: dict):
    # Only insert zone if zone_id is provided
    if zone_id is not None:
        cur.execute("SELECT id FROM zones WHERE id = %s", (zone_id,))
        if not cur.fetchone():
            cur.execute("INSERT INTO zones (id, name) VALUES (%s, %s)", (zone_id, f"Zona {zone_id}"))

    # Ensure node exists (nullable zone_id and location)
    cur.execute("SELECT id FROM processor_nodes WHERE id = %s", (node_id,))
    if not cur.fetchone():
        if location:
            lon, lat = location['coordinates']
            cur.execute("""
                INSERT INTO processor_nodes (id, zone_id, location)
                VALUES (%s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
            """, (node_id, zone_id, lon, lat))
        else:
            cur.execute("INSERT INTO processor_nodes (id, zone_id) VALUES (%s, %s)", (node_id, zone_id))

def ensure_container(cur, container_id: str, node_id: str, zone_id: str | None, location: dict):
    cur.execute("SELECT id FROM containers WHERE id = %s", (container_id,))
    if not cur.fetchone():
        if location:
            lon, lat = location['coordinates']
            cur.execute("""
                INSERT INTO containers (id, node_id, zone_id, type, created_at, location)
                VALUES (%s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))
            """, (container_id, node_id, zone_id, "simulated", datetime.now(), lon, lat))
        else:
            cur.execute("""
                INSERT INTO containers (id, node_id, zone_id, type, created_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (container_id, node_id, zone_id, "simulated", datetime.now()))

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        node_id = payload.get("node_id")
        container_id = payload.get("container_id")
        fill_level = payload.get("fill_level")
        timestamp = payload.get("timestamp")
        location = payload.get("location")  # {"type": "Point", "coordinates": [lon, lat]}

        if not all([node_id, container_id, timestamp, fill_level]):
            print("Datos incompletos")
            return

        with get_conn() as conn:
            cur = conn.cursor()

            # Fetch zone_id for the node if exists (nullable)
            cur.execute("SELECT zone_id FROM processor_nodes WHERE id = %s", (node_id,))
            result = cur.fetchone()
            zone_id = result[0] if result and result[0] else None

            ensure_zone_and_node(cur, zone_id, node_id, location)
            ensure_container(cur, container_id, node_id, zone_id, location)

            cur.execute("""
                INSERT INTO container_readings (container_id, fill_level, timestamp, received_at)
                VALUES (%s, %s, %s, %s)
            """, (container_id, fill_level, timestamp, datetime.now()))

            conn.commit()
            print(f"Procesado: {container_id} - {fill_level}%")

    except Exception as e:
        print(f"Error procesando mensaje: {e}")

def on_disconnect(client, userdata, reason_code, properties=None):
    if reason_code != 0:
        print("MQTT disconnected unexpectedly. Trying to reconnect...")
        while not should_exit:
            try:
                client.reconnect()
                print("Reconnected to MQTT broker.")
                break
            except Exception as e:
                print(f"Reconnect failed: {e}")
                time.sleep(5)

def signal_handler(sig, frame):
    global should_exit
    print("Signal received, shutting down gracefully...")
    should_exit = True
    client.loop_stop()
    client.disconnect()
    sys.exit(0)

def start_worker():
    global client

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    client.on_message = on_message
    client.on_disconnect = on_disconnect

    # Retry until connected (initial attempt)
    while not should_exit:
        try:
            client.connect(MQTT_BROKER, MQTT_PORT, 60)
            print("Connected to MQTT broker.")
            break
        except Exception as e:
            print(f"Initial MQTT connection failed: {e}")
            time.sleep(5)

    client.subscribe(MQTT_TOPIC)
    print("Subscribed to topic:", MQTT_TOPIC)

    client.loop_start()

    # Wait for shutdown
    while not should_exit:
        signal.pause()

if __name__ == "__main__":
    start_worker()