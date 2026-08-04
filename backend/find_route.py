import asyncio
from app.infrastructure.database.connection import async_session
from sqlalchemy import select
from app.infrastructure.database.models import TrainStop, Station

async def find_valid_route():
    async with async_session() as session:
        # Get a couple of train stops to find valid stations
        stmt = select(TrainStop, Station).join(Station).limit(10)
        result = await session.execute(stmt)
        stops = result.all()
        for stop, station in stops:
            print(f"Train {stop.train_route_id} at {station.code} ({station.name})")

if __name__ == "__main__":
    asyncio.run(find_valid_route())
