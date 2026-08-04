from __future__ import annotations
import hashlib
from datetime import date
from app.domain.interfaces.repositories import IAvailabilityProvider
from app.domain.value_objects.enums import SeatStatus

class MockAvailabilityProvider(IAvailabilityProvider):
    POPULAR_ROUTES = [
        "12951", "12952", "12003", "12004", "12301", "12302"
    ]

    async def get_availability(self, train_number: str, from_code: str, to_code: str, travel_date: date, travel_class: str) -> SeatStatus:
        hash_input = f"{train_number}_{from_code}_{to_code}_{travel_date.isoformat()}_{travel_class}".encode('utf-8')
        hash_val = int(hashlib.md5(hash_input).hexdigest(), 16)
        
        score = (hash_val % 100) + 1
        
        if train_number in self.POPULAR_ROUTES:
            if score > 80:
                return SeatStatus.AVAILABLE
            elif score > 40:
                return SeatStatus.RAC
            elif score > 10:
                return SeatStatus.WAITLISTED
            else:
                return SeatStatus.NOT_AVAILABLE
        else:
            if score > 40:
                return SeatStatus.AVAILABLE
            elif score > 20:
                return SeatStatus.RAC
            elif score > 5:
                return SeatStatus.WAITLISTED
            else:
                return SeatStatus.NOT_AVAILABLE
