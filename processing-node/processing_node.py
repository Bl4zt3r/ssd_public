from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta
from sqlalchemy import (
    create_engine, Column, String, Integer,
    Float, Boolean, TIMESTAMP, ForeignKey, func
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import threading
import time
import os
import requests
import pytz
import logging

# --- Logging setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# --- Config ---
CENTRAL_SERVER_URL = os.getenv("CENTRAL_SERVER_URL", "http://central-server:8000/receive")
TIMEZONE = os.getenv("TZ", "America/Santiago")
TZ = pytz.timezone(TIMEZONE)

# --- Database setup ---
DATABASE_URL = "sqlite:////db/data.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
from sqlalchemy.orm import declarative_base
Base = declarative_base()

# --- ORM Models ---
class Container(Base):
    __tablename__ = "containers"
    id = Column(String, primary_key=True)
    type = Column(String)
    sensors = relationship("Sensor", back_populates="container")

class Sensor(Base):
    __tablename__ = "sensors"
    id = Column(String, primary_key=True)
    container_id = Column(String, ForeignKey("containers.id"))
    installed_at = Column(TIMESTAMP)
    container = relationship("Container", back_populates="sensors")

class LevelData(Base):
    __tablename__ = "level_data"
    id = Column(Integer, primary_key=True, autoincrement=True)
    container_id = Column(String, ForeignKey("containers.id"))
    timestamp = Column(TIMESTAMP)
    is_sent = Column(Boolean, default=False)
    fill_level = Column(Float)
    created_at = Column(TIMESTAMP, default=func.now())

class RawSensorData(Base):
    __tablename__ = "raw_sensor_data"
    id = Column(Integer, primary_key=True, autoincrement=True)
    sensor_id = Column(String, ForeignKey("sensors.id"))
    container_id = Column(String, ForeignKey("containers.id"))
    level_id = Column(Integer, ForeignKey("level_data.id"), nullable=True)
    timestamp = Column(TIMESTAMP)
    fill_level = Column(Float)
    received_at = Column(TIMESTAMP, default=func.now())

Base.metadata.create_all(bind=engine)
logger.info("Database and tables created.")

# --- FastAPI setup ---
app = FastAPI()
logger.info("FastAPI app initialized.")

# --- Pydantic Input Model ---
class Measurement(BaseModel):
    fill_level: float
    timestamp: int

class SensorPacket(BaseModel):
    sensor_id: str
    measurements: List[Measurement]

@app.post("/push")
async def push_data(packet: SensorPacket):
    logger.info(f"Received data from sensor {packet.sensor_id} with {len(packet.measurements)} measurements.")
    db = SessionLocal()
    try:
        # Ensure sensor and container exist
        sensor = db.query(Sensor).filter(Sensor.id == packet.sensor_id).first()
        if not sensor:
            logger.info(f"Sensor {packet.sensor_id} not found. Creating new sensor and container.")
            container_id = f"container_{packet.sensor_id}"
            if not db.query(Container).filter_by(id=container_id).first():
                db.add(Container(id=container_id, type="simulated"))
            sensor = Sensor(id=packet.sensor_id, container_id=container_id, installed_at=datetime.now(TZ))
            db.add(sensor)
            db.commit()
        for m in packet.measurements:
            db.add(RawSensorData(
                sensor_id=packet.sensor_id,
                container_id=sensor.container_id,
                timestamp=datetime.fromtimestamp(m.timestamp, TZ),
                fill_level=m.fill_level
            ))
        db.commit()
        logger.info("Measurements stored successfully.")
    except Exception as e:
        logger.error(f"Error processing data from sensor {packet.sensor_id}: {e}")
    finally:
        db.close()
    return {"status": "ok"}

# --- Background aggregation and sending task ---
def aggregate_and_send():
    logger.info("Background aggregation task started.")
    while True:
        db = SessionLocal()
        try:
            # Remove data older than 24h
            cutoff = datetime.now(TZ) - timedelta(hours=24)
            deleted = db.query(RawSensorData).filter(RawSensorData.timestamp < cutoff).delete()
            if deleted:
                logger.info(f"Deleted {deleted} old raw data records.")
            db.commit()

            containers = db.query(Container).all()
            now = datetime.now(TZ)
            window_start = now - timedelta(seconds=30)

            for container in containers:
                data = db.query(RawSensorData).filter(
                    RawSensorData.container_id == container.id,
                    RawSensorData.timestamp >= window_start,
                    RawSensorData.timestamp <= now
                ).all()

                if data:
                    avg_fill = sum(d.fill_level for d in data) / len(data)
                    level_data = LevelData(
                        container_id=container.id,
                        timestamp=now,
                        fill_level=round(avg_fill, 2)
                    )
                    db.add(level_data)
                    db.commit()

                    for d in data:
                        d.level_id = level_data.id
                    db.commit()
                    logger.info(f"Aggregated level data stored for container {container.id}.")

            # Send unsent data
            unsent = db.query(LevelData).filter_by(is_sent=False).all()
            for entry in unsent:
                try:
                    payload = {
                        "container_id": entry.container_id,
                        "timestamp": entry.timestamp.isoformat(),
                        "fill_level": entry.fill_level,
                        "created_at": entry.created_at.isoformat()
                    }
                    response = requests.post(CENTRAL_SERVER_URL, json=payload, timeout=5)
                    if response.status_code == 200:
                        entry.is_sent = True
                        db.commit()
                        logger.info(f"Sent data for container {entry.container_id} to central server.")
                    else:
                        logger.warning(f"Failed to send data for container {entry.container_id}, status code {response.status_code}.")
                except Exception as e:
                    logger.error(f"Failed to send data for container {entry.container_id}: {e}")
        except Exception as e:
            logger.error(f"Error in aggregation/send: {e}")
        finally:
            db.close()

        time.sleep(300)  # Every 5 minutes

# --- Start background thread ---
threading.Thread(target=aggregate_and_send, daemon=True).start()
logger.info("Processing node is running.")
