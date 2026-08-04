from __future__ import annotations
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
