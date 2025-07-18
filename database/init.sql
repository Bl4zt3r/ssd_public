-- Habilitar PostGIS si no existe
CREATE EXTENSION IF NOT EXISTS postgis;

-- Tabla de datos de zonas (zones)
CREATE TABLE IF NOT EXISTS zones (
    id TEXT PRIMARY KEY,
    name TEXT,
    boundary GEOGRAPHY(POLYGON)
);

-- Tabla de datos de nodos de procesamiento (processor_nodes)
CREATE TABLE IF NOT EXISTS processor_nodes (
    id TEXT PRIMARY KEY,
    zone_id TEXT REFERENCES zones(id),
    location GEOGRAPHY(POINT)
);

-- Tabla de contenedores (containers)
CREATE TABLE IF NOT EXISTS containers (
    id TEXT PRIMARY KEY,
    node_id TEXT REFERENCES processor_nodes(id),
    zone_id TEXT REFERENCES zones(id),
    type TEXT,
    location GEOGRAPHY(POINT),
    created_at TIMESTAMP
);

-- Tabla de datos de nivel (level_data)
CREATE TABLE IF NOT EXISTS level_data (
    id SERIAL PRIMARY KEY,
    node_id TEXT REFERENCES processor_nodes(id),
    container_id TEXT REFERENCES containers(id),
    timestamp TIMESTAMP,
    fill_level FLOAT,
    location GEOGRAPHY(POINT),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de datos de lecturas (container_readings)
CREATE TABLE IF NOT EXISTS container_readings (
    id SERIAL PRIMARY KEY,
    container_id TEXT REFERENCES containers(id),
    fill_level FLOAT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    received_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Índices recomendados
CREATE INDEX IF NOT EXISTS idx_level_data_timestamp ON level_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_containers_location ON containers USING GIST (location);
