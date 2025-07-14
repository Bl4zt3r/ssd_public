
# 📦 SCED Containers — Edge-to-Cloud Distributed System

El sistema **SCED Containers** implementa una arquitectura distribuida **edge-to-cloud** con múltiples componentes, configuraciones específicas y secuencias de ejecución coordinadas para garantizar un despliegue y funcionamiento robusto.

---

## ⚙️ Configuración Avanzada del Entorno

### Variables de Entorno Críticas

- **Nodo de procesamiento:** Usa `CENTRAL_SERVER_URL` para conectarse al servidor central (`docker-compose.edge.yml:6`).
- **Simuladores de sensores:** Requieren `CONTAINER_ID`, `SENSOR_ID` y `SERVER_ADDR` individuales (`docker-compose.edge.yml:18-20`).
- **Servidor:** Base de datos PostgreSQL inicializada con `init.sql` (`docker-compose.server.yml:14`). El backend crea tablas automáticamente si no existen (`main.py:27-47`).

### Configuración de Redes Avanzada

- Usa redes Docker separadas (`sced-server-net`, `sced-edge-net`) o una red compartida (`distri2`) para aislar o comunicar componentes de forma controlada.
- La URL externa configurada en `CENTRAL_SERVER_URL` permite la comunicación entre edge y servidor.

---

## 🗃️ Configuración de Base de Datos

- Motor: **PostgreSQL + PostGIS**
- Script: `init.sql` crea `containers` y `level_data`
- Backend: inicializa tablas en tiempo de ejecución si no existen.

---

## 🚀 Secuencia de Ejecución Completa

### 1️⃣ Preparación del Entorno

```bash
# Crear estructura de directorios
mkdir -p processing-node_volume database mqtt

# Configurar variables de entorno
cat > .env << EOF
POSTGRES_DB=sced
POSTGRES_USER=sced_user
POSTGRES_PASSWORD=securepass
EOF
```

### 2️⃣ Ejecución del Entorno Servidor (orden crítico)

```bash
# Iniciar infraestructura
docker-compose -f docker-compose.server.yml up -d db mqtt

# Esperar inicialización
sleep 10

# Iniciar backend, worker y frontend
docker-compose -f docker-compose.server.yml up -d backend worker frontend
```

### 3️⃣ Ejecución del Entorno Edge

```bash
# Iniciar nodo de procesamiento
docker-compose -f docker-compose.edge.yml up -d processing_node

# Verificar logs y conectividad
docker-compose -f docker-compose.edge.yml logs processing_node

# Iniciar simuladores
docker-compose -f docker-compose.edge.yml up -d sensor_simulator_c1a1 sensor_simulator_c1a2 sensor_simulator_c1a3
```

---

## 🔄 Flujo de Datos Detallado

| Etapa | Detalles |
|-------|----------|
| 🛰️ **Simulación de Sensores** | Generan datos cada 3s con valores aleatorios 0–100 (`sensor_simulator.py:20-23`). Mantienen un buffer de 10 mediciones (`sensor_simulator.py:26-28`). |
| 🗂️ **Procesamiento Local** | Nodo recibe `POST /push` y almacena en SQLite (`processing_node.py:85-112`). Agrega promedios cada 30s, envía cada 1 min (`processing_node.py:120-151`). |
| ☁️ **Transmisión al Servidor Central** | Datos agregados enviados vía `HTTP POST` (`processing_node.py:154-172`). Ingestor almacena en MQTT (`ingestor.py:22-51`). |
| 🔁 **Análisis de Datos** | Worker procesa continuamente promedios cada 5 min (`worker.py:51-84`). |


---

## 🔍 Monitoreo y Verificación

```bash
# Estado de servicios
docker-compose -f docker-compose.server.yml ps
docker-compose -f docker-compose.edge.yml ps

# Logs de procesamiento
docker-compose -f docker-compose.edge.yml logs -f processing_node

# Verificar datos en PostgreSQL
docker exec -it ssd_public_db_1 psql -U sced_user -d sced -c "SELECT * FROM level_data ORDER BY timestamp DESC LIMIT 10;"
```

---

## 🗄️ Persistencia de Datos

| Componente | Motor | Detalle |
|------------|-------|---------|
| **Edge** | SQLite | Ubicación: `./processing-node_volume:/db`. TTL: 24h. Buffer local y agregación. |
| **Servidor** | PostgreSQL + PostGIS | Puerto: 5432. Tablas: `containers` y `level_data`. Almacenamiento permanente y consultas. |

---

## 🧩 Notas

- La arquitectura distribuida requiere sincronización cuidadosa.
- El nodo de procesamiento almacena localmente para garantizar continuidad en caso de fallos de red.
- Los simuladores implementan buffer para reenviar datos tras caídas de red.
- El sistema es resiliente a fallos de nodos gracias a almacenamiento local y reintentos automáticos.

---

## 📚 Referencias

- `docker-compose.edge.yml:7` — Configuración del `CENTRAL_SERVER_URL`.
- `docker-compose.edge.yml:18-21` — Variables de cada simulador.
- `docker-compose.server.yml:13` — Inicialización de la base de datos.
- `db.py` — Creación automática de tablas.
- `sensor_simulator.py` y `processing_node.py` — Lógica de simulación, buffer y transmisión.

---

## 🚀 Todo Listo

Con estos pasos tienes un entorno **edge-to-cloud** robusto y resiliente, listo para monitorear contenedores de forma distribuida.

¡Despliégalo y experimenta la potencia de SCED Containers! 🚀✨
