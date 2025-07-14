import { useEffect, useState } from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  GeoJSON,
  CircleMarker,
} from "react-leaflet";
import { z } from "zod";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

delete L.Icon.Default.prototype._getIconUrl;

L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});
function fillLevelToColor(fillLevel) {
  const level = Math.min(100, Math.max(0, fillLevel));

  if (level < 50) {
    const ratio = level / 50;
    const r = Math.round(255 * ratio);
    const g = 255;
    const b = 0;
    return `rgb(${r},${g},${b})`;
  } else {
    const ratio = (level - 50) / 50;
    const r = 255;
    const g = Math.round(255 * (1 - ratio));
    const b = 0;
    return `rgb(${r},${g},${b})`;
  }
}

const radius = (fillLevel) => 8 + (fillLevel / 100) * 12;

// Define schema
const ReadingSchema = z.object({
  container_id: z.string(),
  fill_level: z.number(),
  timestamp: z.string().refine((str) => !isNaN(Date.parse(str)), {
    message: "Invalid date string",
  }),
  received_at: z.string().refine((str) => !isNaN(Date.parse(str)), {
    message: "Invalid date string",
  }),
  lon: z.number(),
  lat: z.number(),
});

const ReadingsSchema = z.array(ReadingSchema);

const ZoneSchema = z.object({
  id: z.string(),
  name: z.string(),
  boundary: z.object({
    type: z.string(),
    coordinates: z.any(),
  }),
});
const ZonesSchema = z.array(ZoneSchema);

export default function App() {
  const [readings, setReadings] = useState([]);
  const [zones, setZones] = useState([]);
  const [timestamps, setTimestamps] = useState([]);
  const [selectedTime, setSelectedTime] = useState("");
  const [view, setView] = useState("map");

  const fetchReadings = () => {
    const queryParams = new URLSearchParams();
    if (selectedTime) {
      queryParams.set("timestamp", selectedTime);
      queryParams.set("range_seconds", "600"); // ±5 minutes
    }

    fetch(`/api/readings?${queryParams.toString()}`)
      .then((r) => r.json())
      .then((data) => {
        try {
          const parsed = ReadingsSchema.parse(data);
          setReadings(parsed);

          if (timestamps.length === 0) {
            const times = Array.from(
              new Set(parsed.map((r) => r.timestamp))
            ).sort();
            setTimestamps(times);
            if (!selectedTime && times.length > 0) {
              setSelectedTime(times[0]);
            }
          }
        } catch (e) {
          console.error("Reading validation error:", e);
        }
      })
      .catch((err) => console.error("Readings fetch error:", err));
  };

  const fetchZones = () => {
    fetch("/api/zones")
      .then((r) => r.json())
      .then((data) => {
        try {
          const parsed = ZonesSchema.parse(data);
          setZones(parsed);
        } catch (e) {
          console.error("Zone validation error:", e);
        }
      })
      .catch((err) => console.error("Zones fetch error:", err));
  };

  useEffect(() => {
    fetchReadings();
    fetchZones();
    const id = setInterval(fetchReadings, 30000);
    return () => clearInterval(id);
  }, []);

  const filtered = selectedTime
    ? readings.filter((r) => r.timestamp === selectedTime)
    : readings;

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <div className="navbar">
        <button
          className={view === "map" ? "active" : ""}
          onClick={() => setView("map")}
        >
          Mapa
        </button>
        <button
          className={view === "table" ? "active" : ""}
          onClick={() => setView("table")}
        >
          Tabla
        </button>
        <div className="header-actions">
          <label>
            Tiempo:&nbsp;
            <select
              value={selectedTime}
              onChange={(e) => setSelectedTime(e.target.value)}
            >
              {timestamps.map((t) => (
                <option key={t} value={t}>
                  {new Date(t).toLocaleString()}
                </option>
              ))}
            </select>
          </label>
          <button onClick={fetchReadings}>Actualizar</button>
        </div>
      </div>

      {view === "map" && (
        <MapContainer center={[-34.07, -70.73]} zoom={14} style={{ flex: 1 }}>
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

          {zones.map((zone) => (
            <GeoJSON
              key={zone.id}
              data={zone.boundary}
              pathOptions={{ color: "blue", weight: 2 }}
            />
          ))}
          {filtered.map((c) => (
            <CircleMarker
              key={c.container_id}
              center={[c.lat, c.lon]}
              radius={radius(c.fill_level)}
              pathOptions={{
                fillColor: fillLevelToColor(c.fill_level),
                color: fillLevelToColor(c.fill_level),
              }}
            >
              <Popup>
                <div>
                  <strong>{c.container_id}</strong>
                  <br />
                  Nivel: {c.fill_level}%<br />
                  {new Date(c.timestamp).toLocaleString()}
                </div>
              </Popup>
            </CircleMarker>
          ))}
          {filtered.map((c) => (
            <Marker key={c.container_id} position={[c.lat, c.lon]}>
              <Popup>
                <div>
                  <strong>{c.container_id}</strong>
                  <br />
                  Nivel: {c.fill_level}%
                  <br />
                  {new Date(c.timestamp).toLocaleString()}
                  <br />
                  {new Date(c.received_at).toLocaleString()}
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      )}

      {view === "table" && (
        <div style={{ flex: 1, overflowY: "auto" }}>
          <h2 style={{ textAlign: "center" }}>Contenedores</h2>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th>ID</th>
                <th>Nivel</th>
                <th>Fecha</th>
                <th>Recibido</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((c) => (
                <tr key={c.container_id}>
                  <td>{c.container_id}</td>
                  <td>{c.fill_level}%</td>
                  <td>{new Date(c.timestamp).toLocaleString()}</td>
                  <td>{new Date(c.received_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
