-- === Schema Definitions ===
CREATE TABLE IF NOT EXISTS zones (
    id TEXT PRIMARY KEY,
    name TEXT,
    boundary GEOGRAPHY(POLYGON)
);

CREATE TABLE IF NOT EXISTS processor_nodes (
    id TEXT PRIMARY KEY,
    zone_id TEXT REFERENCES zones(id),
    location GEOGRAPHY(POINT)
);

CREATE TABLE IF NOT EXISTS containers (
    id TEXT PRIMARY KEY,
    node_id TEXT REFERENCES processor_nodes(id),
    zone_id TEXT REFERENCES zones(id),
    type TEXT,
    location GEOGRAPHY(POINT),
    created_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS level_data (
    id SERIAL PRIMARY KEY,
    node_id TEXT REFERENCES processor_nodes(id),
    container_id TEXT REFERENCES containers(id),
    timestamp TIMESTAMP,
    fill_level FLOAT,
    location GEOGRAPHY(POINT),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS container_readings (
    id SERIAL PRIMARY KEY,
    container_id TEXT REFERENCES containers(id),
    fill_level FLOAT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    received_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- === Sample Data Inserts ===

-- Insert sample zone for Graneros
INSERT INTO zones (id, name, boundary) VALUES
('ZONA-GRANEROS-CL-VI', 'Graneros, O’Higgins, Chile',
 ST_GeogFromText(
   'POLYGON((' ||
   '-70.7400 -34.0750, ' ||
   '-70.7200 -34.0750, ' ||
   '-70.7200 -34.0600, ' ||
   '-70.7400 -34.0600, ' ||
   '-70.7400 -34.0750))'
 ))
ON CONFLICT (id) DO NOTHING;

-- Insert one processor node within the zone
INSERT INTO processor_nodes (id, zone_id, location) VALUES
('NODO-GR-001', 'ZONA-GRANEROS-CL-VI',
 ST_GeogFromText('POINT(-70.7300 -34.0675)'))
ON CONFLICT (id) DO NOTHING;

-- Insert one container at the same location as the node
INSERT INTO containers (id, node_id, zone_id, type, location, created_at) VALUES
('CONTENEDOR-GR-C001', 'NODO-GR-001', 'ZONA-GRANEROS-CL-VI',
 'mixed', ST_GeogFromText('POINT(-70.7300 -34.0675)'), NOW())
ON CONFLICT (id) DO NOTHING;