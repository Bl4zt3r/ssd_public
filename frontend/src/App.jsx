import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';

export default function App() {
  const [data, setData] = useState([]);
  const [view, setView] = useState('map');

  const fetchData = () => {
    fetch('/api/contenedores').then(r => r.json()).then(setData);
  };

  useEffect(() => {
    fetchData();
    const id = setInterval(fetchData, 30000);
    return () => clearInterval(id);
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      <div className="navbar">
        <button className={view === 'map' ? 'active' : ''} onClick={() => setView('map')}>Mapa</button>
        <button className={view === 'table' ? 'active' : ''} onClick={() => setView('table')}>Tabla</button>
        <div className="header-actions">
          <button onClick={fetchData}>Actualizar</button>
        </div>
      </div>
      {view === 'map' && (
        <MapContainer center={[0, 0]} zoom={2} style={{ flex: 1 }}>
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
          {data.map(c => (
            <Marker key={c.id} position={[0, 0]}>
              <Popup>
                <div>
                  <strong>{c.id}</strong>
                  <br />Nivel: {c.nivel}%
                  <br />Temp: {c.temp}°C
                  <br />Gases: {c.gases}%
                  <br />{new Date(c.fecha).toLocaleString()}
                </div>
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      )}
      {view === 'table' && (
        <div style={{ flex: 1, overflowY: 'auto' }}>
          <h2 style={{ textAlign: 'center' }}>Contenedores</h2>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th>ID</th>
                <th>Nivel</th>
                <th>Temp</th>
                <th>Gases</th>
                <th>Fecha</th>
              </tr>
            </thead>
            <tbody>
              {data.map(c => (
                <tr key={c.id}>
                  <td>{c.id}</td>
                  <td>{c.nivel}%</td>
                  <td>{c.temp}°C</td>
                  <td>{c.gases}%</td>
                  <td>{new Date(c.fecha).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
