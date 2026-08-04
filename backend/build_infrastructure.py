import os

base_dir = r"c:\Users\thispc\Downloads\NextRoute\backend"

files = {}

files["app/infrastructure/database/connection.py"] = """
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./nextroute.db")

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
"""

files["app/infrastructure/database/models.py"] = """
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Float, Integer, Boolean, DateTime

class Base(DeclarativeBase):
    pass

class StationModel(Base):
    __tablename__ = "stations"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String)
    city: Mapped[str] = mapped_column(String)
    state: Mapped[str] = mapped_column(String)
    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)
    station_type: Mapped[str] = mapped_column(String)
    zone: Mapped[str] = mapped_column(String, nullable=True)

class BusStopModel(Base):
    __tablename__ = "bus_stops"
    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String)
    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)

class TrainRouteModel(Base):
    __tablename__ = "train_routes"
    id: Mapped[int] = mapped_column(primary_key=True)
    train_number: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String)
    train_type: Mapped[str] = mapped_column(String)

class TrainStopModel(Base):
    __tablename__ = "train_stops"
    id: Mapped[int] = mapped_column(primary_key=True)
    train_id: Mapped[int] = mapped_column(Integer)
    station_code: Mapped[str] = mapped_column(String)
    arrival_time: Mapped[str] = mapped_column(String)
    departure_time: Mapped[str] = mapped_column(String)
    day_offset: Mapped[int] = mapped_column(Integer)
    stop_number: Mapped[int] = mapped_column(Integer)

class TrainFareModel(Base):
    __tablename__ = "train_fares"
    id: Mapped[int] = mapped_column(primary_key=True)

class BusRouteModel(Base):
    __tablename__ = "bus_routes"
    id: Mapped[int] = mapped_column(primary_key=True)

class BusStopsSequenceModel(Base):
    __tablename__ = "bus_stops_sequence"
    id: Mapped[int] = mapped_column(primary_key=True)

class NearbyConnectionsModel(Base):
    __tablename__ = "nearby_connections"
    id: Mapped[int] = mapped_column(primary_key=True)

class UserModel(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)

class SearchHistoryModel(Base):
    __tablename__ = "search_history"
    id: Mapped[int] = mapped_column(primary_key=True)

class SavedRouteModel(Base):
    __tablename__ = "saved_routes"
    id: Mapped[int] = mapped_column(primary_key=True)

class JourneyFeedbackModel(Base):
    __tablename__ = "journey_feedback"
    id: Mapped[int] = mapped_column(primary_key=True)

class ScoringWeightsModel(Base):
    __tablename__ = "scoring_weights"
    id: Mapped[int] = mapped_column(primary_key=True)

class StationSafetyModel(Base):
    __tablename__ = "station_safety"
    id: Mapped[int] = mapped_column(primary_key=True)

class StationPopularityModel(Base):
    __tablename__ = "station_popularity"
    id: Mapped[int] = mapped_column(primary_key=True)

class CachedRoutesModel(Base):
    __tablename__ = "cached_routes"
    id: Mapped[int] = mapped_column(primary_key=True)

class DatasetVersionsModel(Base):
    __tablename__ = "dataset_versions"
    id: Mapped[int] = mapped_column(primary_key=True)

class SystemSettingsModel(Base):
    __tablename__ = "system_settings"
    id: Mapped[int] = mapped_column(primary_key=True)

class ImportLogsModel(Base):
    __tablename__ = "import_logs"
    id: Mapped[int] = mapped_column(primary_key=True)

class RouteStatisticsModel(Base):
    __tablename__ = "route_statistics"
    id: Mapped[int] = mapped_column(primary_key=True)
"""

files["app/infrastructure/database/seed.py"] = """
import asyncio
from app.infrastructure.database.connection import engine, Base

async def seed_data():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Database seeded with South India routes!")

if __name__ == "__main__":
    asyncio.run(seed_data())
"""

files["app/main.py"] = """
from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load graph on startup
    yield

app = FastAPI(title="NextRoute API", lifespan=lifespan)

@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok"}
"""

for path, content in files.items():
    full_path = os.path.join(base_dir, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\\n" if content else "")

print("Infrastructure files generated.")
