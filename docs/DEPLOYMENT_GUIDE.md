# NextRoute Production Deployment Guide

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
