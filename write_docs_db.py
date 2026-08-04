import os

ALEMBIC_MIGRATION = '''"""add missing indexes

Revision ID: add_missing_indexes_1
Revises: 
Create Date: 2026-08-05 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_missing_indexes_1'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Train stops
    op.create_index('ix_train_stops_station_id', 'train_stops', ['station_id'], unique=False)
    # Bus stop sequence
    op.create_index('ix_bus_stops_sequence_bus_stop_id', 'bus_stops_sequence', ['bus_stop_id'], unique=False)
    # Nearby connections
    op.create_index('ix_nearby_connections_station_id', 'nearby_connections', ['station_id'], unique=False)
    op.create_index('ix_nearby_connections_bus_stop_id', 'nearby_connections', ['bus_stop_id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_nearby_connections_bus_stop_id', table_name='nearby_connections')
    op.drop_index('ix_nearby_connections_station_id', table_name='nearby_connections')
    op.drop_index('ix_bus_stops_sequence_bus_stop_id', table_name='bus_stops_sequence')
    op.drop_index('ix_train_stops_station_id', table_name='train_stops')
'''

README = '''# NextRoute: Intelligent Alternate Travel Planner

NextRoute is an advanced, multimodal travel planning platform designed to autonomously discover and rank combinations of Train, Bus, and Walking routes across South India.

## Project Overview
NextRoute calculates routes using Yen’s K-Shortest Path algorithm on a complex Multi-Directed Graph network. It then evaluates the resulting journeys using multiple scoring engines (Safety, Comfort, Cost, Reliability) weighted by user demographics.

## Architecture
Our platform uses Clean Architecture:
- **Flutter App (Frontend)**: Material 3, Riverpod State Management, Hive local offline caching.
- **FastAPI (Backend)**: Python 3.11, Pydantic, Gunicorn, NetworkX graph processing in memory.
- **PostgreSQL / Redis**: Robust storage and sub-millisecond route caching.

## Local Development Setup
1. **Backend**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # or venv\\Scripts\\activate on Windows
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```
2. **Frontend**:
   ```bash
   cd frontend
   flutter pub get
   flutter run
   ```

## Production Docker Deployment
See our [Deployment Guide](docs/DEPLOYMENT_GUIDE.md) for full instructions on spinning up the platform via Docker.

## Testing
Run backend unit/integration tests:
```bash
pytest backend/tests/
```
Run frontend widget tests:
```bash
flutter test frontend/test/
```
'''

DEPLOYMENT_GUIDE = '''# NextRoute Production Deployment Guide

NextRoute's backend is fully containerized using Docker and `docker-compose`.

## Prerequisites
- A Linux server (e.g., AWS EC2, DigitalOcean Droplet)
- Docker & Docker Compose installed.

## 1. Environment Configuration
Create a `.env` file in the root directory:
```env
ENVIRONMENT=prod
POSTGRES_USER=nextroute_admin
POSTGRES_PASSWORD=securepassword123
POSTGRES_DB=nextroute_prod
SECRET_KEY=generate_a_secure_random_key_here
CORS_ORIGINS=["https://your-frontend-domain.com"]
```

## 2. Docker Deployment
Spin up the entire stack (FastAPI, Postgres, Redis):
```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

## 3. Database Migration
Once the containers are running, you must execute the Alembic migrations to build the schema inside the Postgres container:
```bash
docker-compose -f docker-compose.prod.yml exec api alembic upgrade head
```

## 4. Verification
Check if the API is healthy:
```bash
curl http://localhost:8000/api/v1/health/
```
It should return a JSON response confirming `environment: prod`.
'''

def write_db_and_docs():
    os.makedirs('backend/alembic/versions', exist_ok=True)
    with open('backend/alembic/versions/add_missing_indexes_1.py', 'w', encoding='utf-8') as f:
        f.write(ALEMBIC_MIGRATION)
        
    os.makedirs('docs', exist_ok=True)
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(README)
    with open('docs/DEPLOYMENT_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(DEPLOYMENT_GUIDE)
    print("Database migrations and Documentation generated.")

if __name__ == "__main__":
    write_db_and_docs()
