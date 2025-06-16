# AGENTS Instructions

These instructions outline the structure and setup of the `sced-containers` project. They provide guidance on how each component should behave and how the system is orchestrated with Docker.

## Directory Structure (summary)

```
sced-containers/
├── backend/
│   ├── app/
│   ├── Dockerfile
│   └── requirements.txt
├── worker/
├── mqtt/
├── frontend/
├── simulator/
├── database/
├── docker-compose.yml
└── README.md
```

## Key Points
1. Sensor simulation publishes MQTT messages every 5 minutes under `sensors/contenedor_X`.
2. Processing node aggregates MQTT data, stores it in SQLite with a TTL of two days and sends summaries to the backend every 15 minutes.
3. Backend is a FastAPI service exposing `POST /api/report` that republishes payloads to `backend/data` via MQTT.
4. Worker subscribes to `backend/data`, validates the payload and stores measurements in PostgreSQL/PostGIS.
5. Frontend uses React and Leaflet to display container states from `GET /api/contenedores`.
6. Services (backend, worker, db, mqtt, frontend, sensor simulator, processing node) are orchestrated via `docker-compose.yml`.
7. Environment variables are defined in `.env` (e.g., `POSTGRES_DB`, `MQTT_HOST`, `BACKEND_URL`).
8. Include test scripts to simulate MQTT disconnects, check SQLite persistence, verify FastAPI reception and Postgres storage.
9. README should describe the system, architecture diagram, how to run everything (`docker-compose up`), API routes, and example payloads.
10. Optionally, CI workflow `ci.yml` can test linting and backend build.

These instructions apply to all files in this repository.
