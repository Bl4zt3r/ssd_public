import os

# --- MQTT Config ---
MQTT_BROKER = os.getenv("MQTT_BROKER", "mqtt")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = "sced/report"

# --- PostgreSQL Config ---
DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_NAME = os.getenv("POSTGRES_DB", "sced")
DB_USER = os.getenv("POSTGRES_USER", "sced_user")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "securepass")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
