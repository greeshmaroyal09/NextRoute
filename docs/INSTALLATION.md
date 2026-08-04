# Installation Guide

## Backend Setup
1. `cd backend`
2. `python -m venv venv`
3. `source venv/bin/activate` (or `venv\Scripts\activate` on Windows)
4. `pip install -r requirements.txt`
5. `python create_db.py` to seed the database and build the Graph.
6. `uvicorn app.main:app --reload`

## Frontend Setup
1. Install Flutter SDK (3.24+)
2. `cd frontend`
3. `flutter pub get`
4. `flutter run`
