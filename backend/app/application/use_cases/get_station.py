from __future__ import annotations


class AutocompleteUseCase:
    async def execute(self, query: str) -> list:
        return []


class NearbyStationsUseCase:
    async def execute(self, lat: float, lon: float) -> dict:
        return {}
