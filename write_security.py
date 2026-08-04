import os

MAIN_LOGGING = '''import logging
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("nextroute")

settings = get_settings()

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(
        f"Method: {request.method} Path: {request.url.path} "
        f"Status: {response.status_code} Time: {process_time:.4f}s"
    )
    return response

@app.get("/api/v1/health/")
def health_check():
    return {"status": "ok", "version": settings.APP_VERSION}
'''

def apply_logging():
    with open('backend/app/main.py', 'w', encoding='utf-8') as f:
        f.write(MAIN_LOGGING)
    print("Part 5 (Logging & Security) applied.")

if __name__ == '__main__':
    apply_logging()
