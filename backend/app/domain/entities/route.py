from __future__ import annotations

from dataclasses import dataclass

from app.domain.value_objects.enums import BusOperator, BusType, TrainType


@dataclass
class TrainRoute:
    id: str
    train_number: str
    train_name: str
    train_type: TrainType
    runs_on: str

    def runs_on_day(self, day_index: int) -> bool:
        if len(self.runs_on) != 7:
            return False
        return self.runs_on[day_index] == "1"


@dataclass
class BusRoute:
    id: str
    route_number: str
    operator: BusOperator
    bus_type: BusType
    frequency_minutes: int
