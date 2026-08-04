from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Coordinate:
    latitude: float
    longitude: float

    def haversine_distance(self, other: Coordinate) -> float:
        """Returns distance in km."""
        R = 6371.0
        lat1 = math.radians(self.latitude)
        lon1 = math.radians(self.longitude)
        lat2 = math.radians(other.latitude)
        lon2 = math.radians(other.longitude)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))
        return R * c
