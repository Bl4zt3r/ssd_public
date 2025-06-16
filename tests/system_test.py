"""
Basic system test for the distributed waste monitoring system.
Simulates sending data from a sensor to the processing node,
then checks that the backend server has received and stored it.
"""

import os
import time
import requests
from datetime import datetime

# Config
PROCESSING_NODE_URL = os.getenv("PROCESSING_NODE_URL", "http://localhost:8001")
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def test_flow():
    # 1️⃣ Simular sensor -> processing_node
    sensor_payload = {
        "sensor_id": "test_sensor",
        "measurements": [
            {"fill_level": 55.5, "timestamp": int(datetime.now().timestamp())}
        ]
    }
    r1 = requests.post(f"{PROCESSING_NODE_URL}/push", json=sensor_payload)
    assert r1.status_code == 200
    print("✅ Sensor data sent to processing node.")

    # 2️⃣ Esperar a que el processing_node agregue y envíe al backend
    print("⏳ Waiting for processing and sending to backend...")
    time.sleep(10)  # depende de tu tiempo de agregación (mínimo 5 min en producción)

    # 3️⃣ Consultar backend para verificar datos
    r2 = requests.get(f"{BACKEND_URL}/api/contenedores")
    assert r2.status_code == 200
    data = r2.json()
    assert any(
        entry["container_id"] == f"container_{sensor_payload['sensor_id']}"
        for entry in data
    )
    print("✅ Backend received and stored data.")

if __name__ == "__main__":
    test_flow()
