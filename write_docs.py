import os

README = """# NextRoute 🚆🚌

NextRoute is a high-performance routing intelligence platform designed to find the smartest ways to travel across South India via multimodal transport (Trains and Buses). Built with FastAPI (Python) and Flutter (Dart).

## Features
- **Core Intelligence**: A multi-layered Graph architecture that balances cost, safety, wait time, and comfort.
- **Multimodal Routing**: NetworkX-powered train and bus network traversal.
- **Explainability Engine**: Transparent badges and sentence explanations for *why* a route is recommended.
- **Offline First Mobile**: High-speed, cached search lookups built with Hive and Riverpod in Flutter.

See `docs/INSTALLATION.md` to get started.
"""

INSTALLATION = """# Installation Guide

## Backend Setup
1. `cd backend`
2. `python -m venv venv`
3. `source venv/bin/activate` (or `venv\\Scripts\\activate` on Windows)
4. `pip install -r requirements.txt`
5. `python create_db.py` to seed the database and build the Graph.
6. `uvicorn app.main:app --reload`

## Frontend Setup
1. Install Flutter SDK (3.24+)
2. `cd frontend`
3. `flutter pub get`
4. `flutter run`
"""

DEV_GUIDE = """# Developer Guide

## Architecture
NextRoute follows strict **Clean Architecture** patterns.
- Backend: Domain -> Application (Use Cases) -> Infrastructure -> Presentation.
- Frontend: Core -> Shared -> Features (Feature-First architecture).

## Workflow
1. Make changes to an Engine in `backend/app/engines`.
2. Run `pytest` to ensure no routing algorithms break.
3. Use `ruff check --fix .` before committing Python code.
"""

API_DOCS = """# API Documentation

## `POST /api/v1/search/routes`
Search for routes between two stations.

**Request**
```json
{
  "from_code": "MDU",
  "to_code": "SBC",
  "date": "2026-08-05",
  "mode": "FASTEST"
}
```

**Response**
Returns an array of `ExplainedJourney` objects containing segments, durations, and overall score badges.

## `GET /api/v1/health`
Check system status and graph node counts.
"""

ARCH_SUMMARY = """# Architecture Summary

NextRoute relies on `NetworkX` mapping the transportation system as a `MultiDiGraph`.
- **Nodes**: Stations / Bus Stops
- **Edges**: Route Segments (Trains/Buses)
- **Scoring**: A weighted factor model aggregating safety, reliability, cost, and duration into a final 0-100 score.
"""

DEPLOYMENT = """# Deployment Guide

1. **Backend**: Containerize using Docker. Deploy to Google Cloud Run or AWS Fargate.
   - Set `DATABASE_URL` to a production PostgreSQL instance.
   - Set `CORS_ORIGINS` to the exact frontend domain.
2. **Frontend**: Build the Flutter app using `flutter build apk` (Android) or `flutter build web` (Web).
3. **Database**: Use Alembic to run database migrations against production.
"""

def write_docs():
    os.makedirs('docs', exist_ok=True)
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(README)
    with open('docs/INSTALLATION.md', 'w', encoding='utf-8') as f:
        f.write(INSTALLATION)
    with open('docs/DEVELOPER_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(DEV_GUIDE)
    with open('docs/API_DOCUMENTATION.md', 'w', encoding='utf-8') as f:
        f.write(API_DOCS)
    with open('docs/ARCHITECTURE_SUMMARY.md', 'w', encoding='utf-8') as f:
        f.write(ARCH_SUMMARY)
    with open('docs/DEPLOYMENT_GUIDE.md', 'w', encoding='utf-8') as f:
        f.write(DEPLOYMENT)
    
    print("Documentation written successfully.")

if __name__ == '__main__':
    write_docs()
