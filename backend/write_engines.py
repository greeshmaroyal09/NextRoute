import os

GRAPH_BUILDER = '''from __future__ import annotations
import networkx as nx
import pickle
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from app.infrastructure.database.models import (
    Station, BusStop, TrainStop, TrainRoute, BusStopSequence, BusRoute, NearbyConnection
)

class GraphBuilder:
    def _time_to_mins(self, time_str: str) -> int:
        if not time_str:
            return 0
        try:
            h, m = map(int, time_str.split(':'))
            return h * 60 + m
        except:
            return 0

    async def build_from_database(self, session: AsyncSession) -> nx.MultiDiGraph:
        G = nx.MultiDiGraph()
        
        # Stations
        stmt_stations = select(Station)
        for st in (await session.execute(stmt_stations)).scalars():
            G.add_node(st.id, code=st.code, name=st.name, lat=st.latitude, lon=st.longitude, 
                       type=st.station_type, zone=st.zone, node_type='station')

        # Bus Stops
        stmt_bus_stops = select(BusStop)
        for bs in (await session.execute(stmt_bus_stops)).scalars():
            G.add_node(bs.id, code=bs.code, name=bs.name, lat=bs.latitude, lon=bs.longitude, node_type='bus_stop')

        # Train Edges
        stmt_train = select(TrainStop, TrainRoute).join(TrainRoute).order_by(TrainStop.train_route_id, TrainStop.stop_sequence)
        result_ts = await session.execute(stmt_train)
        
        prev_stop = None
        for stop, route in result_ts.all():
            if prev_stop and prev_stop.train_route_id == stop.train_route_id:
                dep_mins = self._time_to_mins(prev_stop.departure_time) + prev_stop.day_offset * 1440
                arr_mins = self._time_to_mins(stop.arrival_time) + stop.day_offset * 1440
                dur = max(0, arr_mins - dep_mins)
                dist = stop.distance_from_origin - prev_stop.distance_from_origin
                
                G.add_edge(
                    prev_stop.station_id, stop.station_id,
                    transport_type='TRAIN', route_id=route.id, train_number=route.train_number,
                    train_name=route.train_name, departure=prev_stop.departure_time, arrival=stop.arrival_time,
                    duration=dur, cost=dist * 0.5, travel_class='GENERAL', frequency=route.runs_on,
                    distance=dist
                )
            prev_stop = stop

        # Bus Edges
        stmt_bus = select(BusStopSequence, BusRoute).join(BusRoute).order_by(BusStopSequence.bus_route_id, BusStopSequence.stop_sequence)
        result_bss = await session.execute(stmt_bus)
        
        prev_bs = None
        for b_stop, b_route in result_bss.all():
            if prev_bs and prev_bs.bus_route_id == b_stop.bus_route_id:
                dep_mins = self._time_to_mins(prev_bs.times)
                arr_mins = self._time_to_mins(b_stop.times)
                dur = max(0, arr_mins - dep_mins)
                # handle overnight bus
                if dur < 0: dur += 1440
                fare_diff = float(b_stop.fare or 0) - float(prev_bs.fare or 0)
                
                G.add_edge(
                    prev_bs.bus_stop_id, b_stop.bus_stop_id,
                    transport_type='BUS', route_id=b_route.id, route_number=b_route.route_number,
                    operator=b_route.operator, bus_type=b_route.bus_type, departure=prev_bs.times,
                    arrival=b_stop.times, duration=dur, cost=max(10.0, fare_diff)
                )
            prev_bs = b_stop

        # Walk Edges
        stmt_nearby = select(NearbyConnection)
        for conn in (await session.execute(stmt_nearby)).scalars():
            u = conn.station_id or conn.bus_stop_id
            v = conn.connected_station_id or conn.connected_bus_stop_id
            if u and v:
                G.add_edge(u, v, transport_type='WALK', distance_meters=conn.distance_meters, 
                           walking_time_minutes=conn.walking_time_minutes, duration=conn.walking_time_minutes, cost=0)

        return G

    def serialize(self, graph: nx.MultiDiGraph, filepath: str) -> None:
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump(graph, f)

    def deserialize(self, filepath: str) -> nx.MultiDiGraph:
        with open(filepath, 'rb') as f:
            return pickle.load(f)

    def get_graph_stats(self, graph: nx.MultiDiGraph) -> dict:
        return {"node_count": graph.number_of_nodes(), "edge_count": graph.number_of_edges()}
'''

ROUTE_ENGINE = '''from __future__ import annotations
import networkx as nx
from datetime import datetime, time, timedelta
from decimal import Decimal
import uuid
import heapq

from app.domain.entities.journey import Journey, JourneySegment
from app.domain.value_objects.enums import TransportType
from app.domain.value_objects.coordinate import Coordinate
from app.config import get_settings

class RouteEngine:
    def __init__(self, graph: nx.MultiDiGraph):
        self._graph = graph
        self._settings = get_settings()

    def _get_nearby_nodes(self, station_code: str) -> list[str]:
        nodes = []
        target_node = None
        for node_id, data in self._graph.nodes(data=True):
            if data.get('code') == station_code:
                target_node = node_id
                break
        if not target_node: return []
        nodes.append(target_node)
        target_coord = Coordinate(lat=self._graph.nodes[target_node]['lat'], lon=self._graph.nodes[target_node]['lon'])
        for node_id, data in self._graph.nodes(data=True):
            if node_id == target_node: continue
            coord = Coordinate(lat=data.get('lat', 0), lon=data.get('lon', 0))
            if target_coord.haversine_distance(coord) <= self._settings.NEARBY_RADIUS_KM:
                nodes.append(node_id)
        return nodes

    def find_routes(self, from_code: str, to_code: str, travel_date: datetime, max_transfers: int = None, allowed_modes: list[str] = None) -> list[Journey]:
        max_transfers = max_transfers or self._settings.MAX_TRANSFERS
        allowed_modes = allowed_modes or ["TRAIN", "BUS"]
        k = self._settings.K_SHORTEST_PATHS
        
        src_nodes = self._get_nearby_nodes(from_code)
        dst_nodes = self._get_nearby_nodes(to_code)
        if not src_nodes or not dst_nodes: return []

        all_paths = []
        dst_set = set(dst_nodes)
        
        for src in src_nodes:
            # Dijkstra-based state: (cost, time, current, path, transfers, last_mode)
            queue = [(0, 0, src, [], 0, None)]
            visited_states = set()
            
            while queue and len(all_paths) < k:
                cost, current_time, current, path, transfers, last_mode = heapq.heappop(queue)
                state_key = (current, transfers, last_mode)
                if state_key in visited_states: continue
                visited_states.add(state_key)
                
                if current in dst_set and path:
                    all_paths.append(path)
                    continue
                
                if transfers >= max_transfers and current not in dst_set:
                    continue
                
                for _, neighbor, edge_key, edge_data in self._graph.edges(current, keys=True, data=True):
                    transport = edge_data.get('transport_type', 'UNKNOWN')
                    if transport == 'WALK':
                        new_mode, added_transfer = last_mode, 0
                    elif transport in allowed_modes:
                        new_mode = transport
                        added_transfer = 1 if last_mode and last_mode != transport else 0
                    else:
                        continue
                    
                    new_transfers = transfers + added_transfer
                    if new_transfers > max_transfers: continue
                    
                    dur = edge_data.get('duration', 60)
                    added_cost = dur + (30 if added_transfer else 0)
                    heapq.heappush(queue, (cost + added_cost, current_time + dur, neighbor, path + [(current, neighbor, edge_data)], new_transfers, new_mode))
        
        journeys = []
        for path in all_paths[:k]:
            journey = self._build_journey(path, travel_date)
            if journey and self._validate_timing(journey):
                journeys.append(journey)
                
        # Return top N by total duration to give scoring engine something reasonable
        journeys.sort(key=lambda j: j.total_duration_minutes)
        return journeys[:self._settings.SEARCH_RESULT_LIMIT * 5]

    def _build_journey(self, path: list, travel_date: datetime) -> Journey | None:
        if not path: return None
        segments = []
        total_cost = Decimal('0')
        transfer_count = 0
        last_transport = None
        base_dt = travel_date.replace(hour=8, minute=0, second=0)
        current_dt = base_dt
        
        for from_node, to_node, edge_data in path:
            transport = edge_data.get('transport_type', 'TRAIN')
            if last_transport and last_transport != transport and transport != 'WALK':
                transfer_count += 1
            if transport != 'WALK':
                last_transport = transport
                
            from_data = self._graph.nodes.get(from_node, {})
            to_data = self._graph.nodes.get(to_node, {})
            
            dur = edge_data.get('duration', 60)
            dep_dt = current_dt
            
            # Use actual departure if available (simplified scheduling for V1)
            dep_str = edge_data.get('departure')
            if dep_str and ":" in dep_str:
                h, m = map(int, dep_str.split(':'))
                new_dep_dt = dep_dt.replace(hour=h, minute=m)
                if new_dep_dt < dep_dt: new_dep_dt += timedelta(days=1)
                dep_dt = new_dep_dt
            
            arr_dt = dep_dt + timedelta(minutes=dur)
            current_dt = arr_dt + timedelta(minutes=self._settings.MIN_TRANSFER_BUFFER_MINS)
            cost = Decimal(str(edge_data.get('cost', 0)))
            total_cost += cost
            
            segments.append(JourneySegment(
                segment_type=TransportType(transport) if transport in TransportType.__members__ else TransportType.TRAIN,
                origin_code=from_data.get('code', from_node),
                origin_name=from_data.get('name', from_node),
                destination_code=to_data.get('code', to_node),
                destination_name=to_data.get('name', to_node),
                departure_time=dep_dt,
                arrival_time=arr_dt,
                duration_minutes=dur,
                distance_km=edge_data.get('distance', 0.0),
                cost_inr=cost,
                travel_class=edge_data.get('travel_class'),
                vehicle_name=edge_data.get('train_name') or edge_data.get('route_number'),
                vehicle_number=edge_data.get('train_number') or edge_data.get('route_number'),
                operator=edge_data.get('operator'),
                seat_status=None
            ))
            
        return Journey(
            journey_id=str(uuid.uuid4()),
            segments=segments,
            total_duration_minutes=sum(s.duration_minutes for s in segments),
            total_cost_inr=total_cost,
            transfer_count=transfer_count
        )

    def _validate_timing(self, journey: Journey) -> bool:
        for i in range(len(journey.segments) - 1):
            gap = (journey.segments[i+1].departure_time - journey.segments[i].arrival_time).total_seconds() / 60
            if gap < self._settings.MIN_TRANSFER_BUFFER_MINS and gap > -1400: # allow next day overlap lenience
                if journey.segments[i].segment_type != TransportType.WALK:
                    return False
        return True
'''

SCORING_ENGINE = '''from __future__ import annotations
from app.domain.entities.journey import Journey, ScoredJourney
from app.engines.safety_engine import SafetyEngine
from app.engines.comfort_engine import ComfortEngine
from app.engines.reliability_engine import ReliabilityEngine
from app.engines.availability_engine import AvailabilityEngine

class ScoringEngine:
    def __init__(self, db_weights: dict):
        self.weights = db_weights
        self.safety_eng = SafetyEngine()
        self.comfort_eng = ComfortEngine()
        self.reliability_eng = ReliabilityEngine()
        self.availability_eng = AvailabilityEngine()

    def rank(self, journeys: list[Journey]) -> list[ScoredJourney]:
        if not journeys: return []
        
        # Calculate raw factors
        raw_factors = []
        for j in journeys:
            rf = {
                "travel_time": float(j.total_duration_minutes),
                "waiting_time": max(0, float((j.arrival_time - j.departure_time).total_seconds() / 60) - j.total_duration_minutes),
                "transfers": float(j.transfer_count),
                "cost": float(j.total_cost_inr),
                "availability": self.availability_eng.calculate(j),
                "comfort": self.comfort_eng.calculate(j),
                "safety": self.safety_eng.calculate(j),
                "reliability": self.reliability_eng.calculate(j),
                "walking_distance": float(sum(s.distance_km for s in j.segments if s.segment_type.value == "WALK")),
                "arrival_penalty": 1.0 if j.arrival_time.hour >= 22 or j.arrival_time.hour < 5 else 0.0
            }
            raw_factors.append((j, rf))
            
        # Min-Max Normalization (0 to 1, higher is better)
        def normalize(key, inverse=False):
            vals = [rf[key] for _, rf in raw_factors]
            min_v, max_v = min(vals), max(vals)
            if min_v == max_v: return [1.0] * len(vals)
            return [1.0 - (v - min_v)/(max_v - min_v) if inverse else (v - min_v)/(max_v - min_v) for v in vals]
            
        norm = {
            "travel_time": normalize("travel_time", True),
            "waiting_time": normalize("waiting_time", True),
            "transfers": normalize("transfers", True),
            "cost": normalize("cost", True),
            "availability": normalize("availability", False),
            "comfort": normalize("comfort", False),
            "safety": normalize("safety", False),
            "reliability": normalize("reliability", False),
            "walking_distance": normalize("walking_distance", True),
            "arrival_penalty": normalize("arrival_penalty", True)
        }
        
        scored = []
        for idx, (j, raw) in enumerate(raw_factors):
            factor_scores = {k: norm[k][idx] for k in norm}
            overall = sum(factor_scores[k] * self.weights.get(k + "_weight", 0.1) for k in factor_scores) * 100
            scored.append(ScoredJourney(journey=j, overall_score=overall, factor_scores=factor_scores, factor_raw_values=raw, rank=0))
            
        scored.sort(key=lambda sj: sj.overall_score, reverse=True)
        for idx, sj in enumerate(scored):
            sj.rank = idx + 1
        return scored
'''

SAFETY_ENGINE = '''from __future__ import annotations
from app.domain.entities.journey import Journey
from app.domain.value_objects.enums import TransportType

class SafetyEngine:
    def calculate(self, journey: Journey) -> float:
        score = 1.0
        # Night travel penalty
        for seg in journey.segments:
            if seg.segment_type == TransportType.WALK:
                if seg.distance_km > 1.0:
                    score -= 0.1
                if seg.departure_time.hour >= 20 or seg.departure_time.hour <= 5:
                    score -= 0.2
            else:
                if seg.arrival_time.hour >= 23 or seg.arrival_time.hour <= 4:
                    score -= 0.1
        
        # Transfers penalty
        score -= min(0.4, journey.transfer_count * 0.1)
        return max(0.1, score)
'''

COMFORT_ENGINE = '''from __future__ import annotations
from app.domain.entities.journey import Journey
from app.domain.value_objects.enums import TransportType

class ComfortEngine:
    TRAIN_COMFORT = {"GENERAL": 0.2, "SLEEPER": 0.4, "AC_3": 0.6, "AC_2": 0.8, "AC_1": 1.0}
    BUS_COMFORT = {"ORDINARY": 0.2, "EXPRESS": 0.4, "SUPER_LUXURY": 0.7, "SLEEPER": 0.9}

    def calculate(self, journey: Journey) -> float:
        if journey.total_duration_minutes == 0: return 1.0
        weighted = 0.0
        for seg in journey.segments:
            cls = seg.travel_class or "GENERAL"
            if seg.segment_type == TransportType.TRAIN:
                c_score = self.TRAIN_COMFORT.get(cls, 0.4)
            elif seg.segment_type == TransportType.BUS:
                c_score = self.BUS_COMFORT.get(cls, 0.4)
            else:
                c_score = 0.5
            weighted += c_score * seg.duration_minutes
        return weighted / journey.total_duration_minutes
'''

RELIABILITY_ENGINE = '''from __future__ import annotations
from app.domain.entities.journey import Journey

class ReliabilityEngine:
    def calculate(self, journey: Journey) -> float:
        score = 1.0
        # More transfers = less reliable
        score -= min(0.5, journey.transfer_count * 0.15)
        # Tight buffer penalty
        for i in range(len(journey.segments) - 1):
            gap = (journey.segments[i+1].departure_time - journey.segments[i].arrival_time).total_seconds() / 60
            if gap > 0 and gap < 30:
                score -= 0.1
        return max(0.1, score)
'''

AVAILABILITY_ENGINE = '''from __future__ import annotations
from app.domain.entities.journey import Journey
from app.domain.value_objects.enums import SeatStatus
import hashlib

class AvailabilityEngine:
    def calculate(self, journey: Journey) -> float:
        # Mock availability based on hash
        h = int(hashlib.md5(journey.journey_id.encode()).hexdigest(), 16) % 100
        if h < 20: return 0.0 # Unavailable
        if h < 50: return 0.2 # WL
        if h < 70: return 0.7 # RAC
        return 1.0 # Available
        
    def populate_segments(self, journey: Journey):
        # Update seat_status on segments
        h = int(hashlib.md5(journey.journey_id.encode()).hexdigest(), 16) % 100
        status = SeatStatus.AVAILABLE
        if h < 20: status = SeatStatus.UNAVAILABLE
        elif h < 40: status = SeatStatus.WL_30_PLUS
        elif h < 70: status = SeatStatus.RAC
        for seg in journey.segments:
            if seg.segment_type.value != "WALK":
                seg.seat_status = status
'''

def write_files():
    os.makedirs("app/infrastructure/graph", exist_ok=True)
    os.makedirs("app/engines", exist_ok=True)
    with open("app/infrastructure/graph/builder.py", "w") as f: f.write(GRAPH_BUILDER)
    with open("app/engines/route_engine.py", "w") as f: f.write(ROUTE_ENGINE)
    with open("app/engines/scoring_engine.py", "w") as f: f.write(SCORING_ENGINE)
    with open("app/engines/safety_engine.py", "w") as f: f.write(SAFETY_ENGINE)
    with open("app/engines/comfort_engine.py", "w") as f: f.write(COMFORT_ENGINE)
    with open("app/engines/reliability_engine.py", "w") as f: f.write(RELIABILITY_ENGINE)
    with open("app/engines/availability_engine.py", "w") as f: f.write(AVAILABILITY_ENGINE)
    print("Files written.")

if __name__ == "__main__":
    write_files()
