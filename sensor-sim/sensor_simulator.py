import os
import time
import random
import requests
from typing import List, NamedTuple
from datetime import datetime
import signal
import sys

ARRAY_LIMIT = 10
CONTAINER_ID = os.getenv("CONTAINER_ID", "unknown")
SENSOR_ID = os.getenv("SENSOR_ID", "unknown")
SERVER_ADDR = os.getenv("SERVER_ADDR", "http://raspberry-pi:5000")
ENDPOINT = f"{SERVER_ADDR}/push"

Measurement = NamedTuple('Measurement', [('fill_level', int), ('timestamp', int)])
measurements: List[Measurement] = []

# Flag to control the main loop
running = True

def handle_shutdown(signum, frame):
    global running
    print(f"\nSignal {signum} received. Shutting down gracefully...")
    running = False

# Register signal handlers for SIGINT (Ctrl+C) and SIGTERM (docker stop)
signal.signal(signal.SIGINT, handle_shutdown)
signal.signal(signal.SIGTERM, handle_shutdown)

print("Starting sensor simulation. Press Ctrl+C to stop.")

while running:
    measurement = Measurement(
        fill_level=random.randint(0, 100),
        timestamp=int(datetime.now().timestamp()),
    )
    measurements.append(measurement)

    if len(measurements) > ARRAY_LIMIT:
        measurements = measurements[1:]

    packet = {
        "sensor_id": SENSOR_ID,
        "container_id": CONTAINER_ID,
        "measurements": [{
            "fill_level": m.fill_level,
            "timestamp": m.timestamp,
        } for m in measurements]
    }

    try:
        response = requests.post(ENDPOINT, json=packet, timeout=5)
        print(f"[{datetime.now()}] Sent packet: {response.status_code}")
        measurements.clear()
    except requests.exceptions.RequestException as e:
        print(f"[{datetime.now()}] Error sending data: {e}")
        print(measurements)

    # Sleep in smaller increments so shutdown is more responsive
    sleep_seconds = 3
    for _ in range(sleep_seconds * 10):  # check every 0.1 seconds
        if not running:
            break
        time.sleep(0.1)

print("Sensor simulation stopped. Exiting.")
sys.exit(0)
