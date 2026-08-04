from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func

from app.domain.value_objects.enums import (
    BusOperator,
    BusType,
    CrowdLevel,
    DatasetStatus,
    LightingQuality,
    StationType,
    TrainType,
    TransferType,
    TravelClass,
    TravelMode,
)


class Base(DeclarativeBase):
    pass


class Station(Base):
    __tablename__ = "stations"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    code: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String)
    city: Mapped[str] = mapped_column(String)
    state: Mapped[str] = mapped_column(String)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    station_type: Mapped[StationType] = mapped_column(SAEnum(StationType))
    zone: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class BusStop(Base):
    __tablename__ = "bus_stops"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    code: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String)
    city: Mapped[str] = mapped_column(String)
    state: Mapped[str] = mapped_column(String)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    operator: Mapped[BusOperator] = mapped_column(SAEnum(BusOperator))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class TrainRoute(Base):
    __tablename__ = "train_routes"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    train_number: Mapped[str] = mapped_column(String, unique=True, index=True)
    train_name: Mapped[str] = mapped_column(String)
    train_type: Mapped[TrainType] = mapped_column(SAEnum(TrainType))
    runs_on: Mapped[str] = mapped_column(String)  # e.g. '1111111'


class TrainStop(Base):
    __tablename__ = "train_stops"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    train_route_id: Mapped[str] = mapped_column(String, ForeignKey("train_routes.id"))
    station_id: Mapped[str] = mapped_column(String, ForeignKey("stations.id"))
    stop_sequence: Mapped[int] = mapped_column(Integer)
    arrival_time: Mapped[str | None] = mapped_column(String, nullable=True)  # HH:MM
    departure_time: Mapped[str | None] = mapped_column(String, nullable=True)
    day_offset: Mapped[int] = mapped_column(Integer, default=0)
    distance_from_origin: Mapped[float] = mapped_column(Float, default=0.0)


class TrainFare(Base):
    __tablename__ = "train_fares"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    train_route_id: Mapped[str] = mapped_column(String, ForeignKey("train_routes.id"))
    from_station_id: Mapped[str] = mapped_column(String, ForeignKey("stations.id"))
    to_station_id: Mapped[str] = mapped_column(String, ForeignKey("stations.id"))
    travel_class: Mapped[TravelClass] = mapped_column(SAEnum(TravelClass))
    fare_inr: Mapped[float] = mapped_column(Numeric(10, 2))


class BusRoute(Base):
    __tablename__ = "bus_routes"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    route_number: Mapped[str] = mapped_column(String, index=True)
    operator: Mapped[BusOperator] = mapped_column(SAEnum(BusOperator))
    bus_type: Mapped[BusType] = mapped_column(SAEnum(BusType))
    frequency_minutes: Mapped[int] = mapped_column(Integer)


class BusStopSequence(Base):
    __tablename__ = "bus_stops_sequence"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    bus_route_id: Mapped[str] = mapped_column(String, ForeignKey("bus_routes.id"))
    bus_stop_id: Mapped[str] = mapped_column(String, ForeignKey("bus_stops.id"))
    stop_sequence: Mapped[int] = mapped_column(Integer)
    times: Mapped[str | None] = mapped_column(String, nullable=True)
    fare: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)


class NearbyConnection(Base):
    __tablename__ = "nearby_connections"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    station_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("stations.id"), nullable=True
    )
    bus_stop_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("bus_stops.id"), nullable=True
    )
    connected_station_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("stations.id"), nullable=True
    )
    connected_bus_stop_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("bus_stops.id"), nullable=True
    )
    distance_meters: Mapped[int] = mapped_column(Integer)
    walking_time_minutes: Mapped[int] = mapped_column(Integer)
    transfer_type: Mapped[TransferType] = mapped_column(SAEnum(TransferType))


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String)
    auth_provider: Mapped[str] = mapped_column(String)
    preferred_mode: Mapped[TravelMode] = mapped_column(SAEnum(TravelMode))


class SearchHistory(Base):
    __tablename__ = "search_history"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("users.id"), nullable=True
    )
    session_id: Mapped[str] = mapped_column(String, index=True)
    from_code: Mapped[str] = mapped_column(String)
    to_code: Mapped[str] = mapped_column(String)
    date: Mapped[datetime] = mapped_column(DateTime)
    params: Mapped[dict] = mapped_column(JSON)
    result_count: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class SavedRoute(Base):
    __tablename__ = "saved_routes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str | None] = mapped_column(
        String, ForeignKey("users.id"), nullable=True
    )
    session_id: Mapped[str] = mapped_column(String, index=True)
    route_name: Mapped[str] = mapped_column(String)
    from_code: Mapped[str] = mapped_column(String)
    to_code: Mapped[str] = mapped_column(String)
    route_data: Mapped[dict] = mapped_column(JSON)
    is_favourite: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class JourneyFeedback(Base):
    __tablename__ = "journey_feedback"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    route_hash: Mapped[str] = mapped_column(String, index=True)
    ratings: Mapped[dict] = mapped_column(JSON)
    would_recommend: Mapped[bool] = mapped_column(Boolean)
    comments: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class ScoringWeight(Base):
    __tablename__ = "scoring_weights"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mode: Mapped[TravelMode] = mapped_column(SAEnum(TravelMode), unique=True)
    travel_time_weight: Mapped[float] = mapped_column(Float)
    waiting_time_weight: Mapped[float] = mapped_column(Float)
    transfers_weight: Mapped[float] = mapped_column(Float)
    cost_weight: Mapped[float] = mapped_column(Float)
    availability_weight: Mapped[float] = mapped_column(Float)
    comfort_weight: Mapped[float] = mapped_column(Float)
    safety_weight: Mapped[float] = mapped_column(Float)
    reliability_weight: Mapped[float] = mapped_column(Float)
    walking_distance_weight: Mapped[float] = mapped_column(Float)
    arrival_penalty_weight: Mapped[float] = mapped_column(Float)


class StationSafety(Base):
    __tablename__ = "station_safety"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    station_id: Mapped[str] = mapped_column(String, ForeignKey("stations.id"))
    cctv: Mapped[bool] = mapped_column(Boolean, default=False)
    waiting_room: Mapped[bool] = mapped_column(Boolean, default=False)
    lighting: Mapped[LightingQuality] = mapped_column(SAEnum(LightingQuality))
    crowd: Mapped[CrowdLevel] = mapped_column(SAEnum(CrowdLevel))
    community_rating: Mapped[float] = mapped_column(Float)


class StationPopularity(Base):
    __tablename__ = "station_popularity"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    station_id: Mapped[str] = mapped_column(String, ForeignKey("stations.id"))
    search_counts: Mapped[int] = mapped_column(Integer, default=0)
    footfall: Mapped[int] = mapped_column(Integer, default=0)
    tier: Mapped[int] = mapped_column(Integer, default=3)


class CachedRoute(Base):
    __tablename__ = "cached_routes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cache_key_hash: Mapped[str] = mapped_column(String, unique=True, index=True)
    result_data: Mapped[dict] = mapped_column(JSON)
    hit_count: Mapped[int] = mapped_column(Integer, default=0)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class DatasetVersion(Base):
    __tablename__ = "dataset_versions"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    version_number: Mapped[str] = mapped_column(String)
    source_type: Mapped[str] = mapped_column(String)
    status: Mapped[DatasetStatus] = mapped_column(SAEnum(DatasetStatus))
    graph_stats: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class SystemSetting(Base):
    __tablename__ = "system_settings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key: Mapped[str] = mapped_column(String, unique=True, index=True)
    value: Mapped[dict] = mapped_column(JSON)
    category: Mapped[str] = mapped_column(String)


class ImportLog(Base):
    __tablename__ = "import_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dataset_version_id: Mapped[str] = mapped_column(
        String, ForeignKey("dataset_versions.id")
    )
    stage: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    message: Mapped[str] = mapped_column(String)
    details: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class RouteStatistic(Base):
    __tablename__ = "route_statistics"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    route_hash: Mapped[str] = mapped_column(String, unique=True, index=True)
    times_recommended: Mapped[int] = mapped_column(Integer, default=0)
    times_selected: Mapped[int] = mapped_column(Integer, default=0)
    times_redirected: Mapped[int] = mapped_column(Integer, default=0)
    scores: Mapped[dict] = mapped_column(JSON)
