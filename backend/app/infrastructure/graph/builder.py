from __future__ import annotations

import pickle
from pathlib import Path

import networkx as nx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models import (
    BusRoute,
    BusStop,
    BusStopSequence,
    NearbyConnection,
    Station,
    TrainRoute,
    TrainStop,
)


class GraphBuilder:
    def _time_to_mins(self, time_str: str) -> int:
        if not time_str:
            return 0
        try:
            h, m = map(int, time_str.split(":"))
            return h * 60 + m
        except:
            return 0

    async def build_from_database(self, session: AsyncSession) -> nx.MultiDiGraph:
        G = nx.MultiDiGraph()

        # Stations
        stmt_stations = select(Station).execution_options(yield_per=1000)
        async for st in (await session.stream(stmt_stations)).scalars():
            G.add_node(
                st.id,
                code=st.code,
                name=st.name,
                lat=st.latitude,
                lon=st.longitude,
                type=st.station_type,
                zone=st.zone,
                node_type="station",
            )

        # Bus Stops
        stmt_bus_stops = select(BusStop).execution_options(yield_per=1000)
        async for bs in (await session.stream(stmt_bus_stops)).scalars():
            G.add_node(
                bs.id,
                code=bs.code,
                name=bs.name,
                lat=bs.latitude,
                lon=bs.longitude,
                node_type="bus_stop",
            )

        # Train Edges
        stmt_train = (
            select(TrainStop, TrainRoute)
            .join(TrainRoute)
            .order_by(TrainStop.train_route_id, TrainStop.stop_sequence)
            .execution_options(yield_per=1000)
        )
        result_ts = await session.stream(stmt_train)

        prev_stop = None
        async for stop, route in result_ts:
            if prev_stop and prev_stop.train_route_id == stop.train_route_id:
                dep_mins = (
                    self._time_to_mins(prev_stop.departure_time)
                    + prev_stop.day_offset * 1440
                )
                arr_mins = (
                    self._time_to_mins(stop.arrival_time) + stop.day_offset * 1440
                )
                dur = max(0, arr_mins - dep_mins)
                dist = stop.distance_from_origin - prev_stop.distance_from_origin

                G.add_edge(
                    prev_stop.station_id,
                    stop.station_id,
                    transport_type="TRAIN",
                    route_id=route.id,
                    train_number=route.train_number,
                    train_name=route.train_name,
                    departure=prev_stop.departure_time,
                    arrival=stop.arrival_time,
                    duration=dur,
                    cost=dist * 0.5,
                    travel_class="GENERAL",
                    frequency=route.runs_on,
                    distance=dist,
                )
            prev_stop = stop

        # Bus Edges
        stmt_bus = (
            select(BusStopSequence, BusRoute)
            .join(BusRoute)
            .order_by(BusStopSequence.bus_route_id, BusStopSequence.stop_sequence)
            .execution_options(yield_per=1000)
        )
        result_bss = await session.stream(stmt_bus)

        prev_bs = None
        async for b_stop, b_route in result_bss:
            if prev_bs and prev_bs.bus_route_id == b_stop.bus_route_id:
                dep_mins = self._time_to_mins(prev_bs.times)
                arr_mins = self._time_to_mins(b_stop.times)
                dur = max(0, arr_mins - dep_mins)
                # handle overnight bus
                if dur < 0:
                    dur += 1440
                fare_diff = float(b_stop.fare or 0) - float(prev_bs.fare or 0)

                G.add_edge(
                    prev_bs.bus_stop_id,
                    b_stop.bus_stop_id,
                    transport_type="BUS",
                    route_id=b_route.id,
                    route_number=b_route.route_number,
                    operator=b_route.operator,
                    bus_type=b_route.bus_type,
                    departure=prev_bs.times,
                    arrival=b_stop.times,
                    duration=dur,
                    cost=max(10.0, fare_diff),
                )
            prev_bs = b_stop

        # Walk Edges
        stmt_nearby = select(NearbyConnection).execution_options(yield_per=1000)
        async for conn in (await session.stream(stmt_nearby)).scalars():
            u = conn.station_id or conn.bus_stop_id
            v = conn.connected_station_id or conn.connected_bus_stop_id
            if u and v:
                G.add_edge(
                    u,
                    v,
                    transport_type="WALK",
                    distance_meters=conn.distance_meters,
                    walking_time_minutes=conn.walking_time_minutes,
                    duration=conn.walking_time_minutes,
                    cost=0,
                )

        return G

    def serialize(self, graph: nx.MultiDiGraph, filepath: str) -> None:
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(graph, f)

    def deserialize(self, filepath: str) -> nx.MultiDiGraph:
        with open(filepath, "rb") as f:
            return pickle.load(f)

    def get_graph_stats(self, graph: nx.MultiDiGraph) -> dict:
        return {
            "node_count": graph.number_of_nodes(),
            "edge_count": graph.number_of_edges(),
        }
