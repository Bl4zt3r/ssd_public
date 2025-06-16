import os
import time
import random
import requests
from typing import List, NamedTuple
from datetime import datetime

ARRAY_LIMIT = 10
CONTAINER_ID = os.getenv("CONTAINER_ID", "unkown")
SENSOR_ID = os.getenv("SENSOR_ID", "unkown")
SERVER_ADDR = os.getenv("SERVER_ADDR", "http://raspberry-pi:5000")
ENDPOINT = f"{SERVER_ADDR}/push"

# Measurements Memory
Measurement = NamedTuple('Measurement', [('fill_level', int), ('timestamp', int)])
measurements: List[Measurement] = []

while True:
    # Create new measurement
    measurement = Measurement(
        fill_level=random.randint(0, 100),
        timestamp=int(datetime.now().timestamp()),
    )
    measurements.append(measurement)

    # Keep list within size limit
    if len(measurements) > ARRAY_LIMIT:
        measurements = measurements[1:]

    # Build data packet
    packet = {
        "sensor_id": SENSOR_ID,
        "container_id": CONTAINER_ID,
        "measurements": [{
            "fill_level": m.fill_level,
            "timestamp": m.timestamp,
        } for m in measurements]
    }

    # Send to server
    try:
        response = requests.post(ENDPOINT, json=packet, timeout=5)
        print(f"[{datetime.now()}] Sent packet: {response.status_code}")
        measurements.clear()
    except requests.exceptions.RequestException as e:
        print(f"[{datetime.now()}] Error sending data: {e}")
        print(measurements)

    # Sleep for 3 seconds
    time.sleep(3)
