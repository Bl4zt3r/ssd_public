-- Habilitar PostGIS si no existe
CREATE EXTENSION IF NOT EXISTS postgis;

-- Tabla de contenedores (containers)
CREATE TABLE IF NOT EXISTS containers (
    id TEXT PRIMARY KEY,
    type TEXT,
    name TEXT,
    location GEOGRAPHY(Point)
);

-- Tabla de datos de nivel (level_data)
CREATE TABLE IF NOT EXISTS level_data (
    id SERIAL PRIMARY KEY,
    container_id TEXT REFERENCES containers(id),
    timestamp TIMESTAMP,
    fill_level FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices recomendados
CREATE INDEX IF NOT EXISTS idx_level_data_timestamp ON level_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_containers_location ON containers USING GIST (location);
