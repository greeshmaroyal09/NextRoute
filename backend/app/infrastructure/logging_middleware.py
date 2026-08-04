from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
import uuid

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] %(message)s')
logger = logging.getLogger("nextroute")

class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        req_id = str(uuid.uuid4())
        
        # Inject request_id into logging context via a thread-safe context var or simple dictionary trick if needed
        # For simplicity in V1, we'll format it directly.
        old_factory = logging.getLogRecordFactory()
        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            record.request_id = req_id
            return record
        logging.setLogRecordFactory(record_factory)

        start_time = time.time()
        logger.info(f"Incoming request: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            logger.info(f"Completed request: {request.method} {request.url.path} - Status: {response.status_code} - Latency: {process_time:.4f}s")
            response.headers["X-Request-ID"] = req_id
            return response
        except Exception as e:
            logger.error(f"Request failed: {request.method} {request.url.path} - Error: {str(e)}", exc_info=True)
            raise e
