# NextRoute: Intelligent Alternate Travel Planner

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
   source venv/bin/activate  # or venv\Scripts\activate on Windows
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
