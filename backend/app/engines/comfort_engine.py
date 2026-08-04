from __future__ import annotations
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
