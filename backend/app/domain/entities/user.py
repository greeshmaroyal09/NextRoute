from __future__ import annotations
from dataclasses import dataclass
from app.domain.value_objects.enums import TravelMode

@dataclass
class User:
    id: str
    email: str
    display_name: str
    auth_provider: str
    preferred_mode: TravelMode
