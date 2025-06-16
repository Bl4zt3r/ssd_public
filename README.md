# SCED Containers

This project simulates a container monitoring platform. Sensors publish readings over MQTT. A processing node aggregates the data and sends summaries to a FastAPI backend which republishes them so a worker can persist them in PostgreSQL/PostGIS. A React/Leaflet frontend displays the latest state of each container.

## Architecture
```
[ESP32 Simulator] --MQTT--> [Processing Node] --HTTP--> [Backend] --MQTT--> [Worker] --PostgreSQL]
                                    |                                                ^
                                    +------------------------- SQLite ----------------+
```

## Run
Clone the repository and start the stack:
```bash
docker-compose up --build
```

You can monitor service logs with:
```bash
docker-compose logs -f
```

## Simulation
Sensor readings can be published manually:
```bash
docker exec -it mqtt mosquitto_pub -t sensors/contenedor_1 -m '{"nivel":75,"temp":30,"gases":50}'
```

## API
- `POST /api/report` – processing node to backend
- `GET /api/contenedores` – latest measurements

The frontend will be available on http://localhost:3000 after build.

Example payload published by the simulator:
```json
{"nivel": 85, "temp": 38, "gases": 32, "timestamp": "2025-01-01T00:00:00", "container_id": "contenedor_1"}
```
