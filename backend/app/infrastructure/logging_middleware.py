import contextvars
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
import uuid

request_id_var = contextvars.ContextVar("request_id", default="system")

class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_var.get()
        return True

# Configure logging
root_logger = logging.getLogger()
# Clear existing handlers to prevent duplicates
root_logger.handlers = []

handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] %(message)s')
handler.setFormatter(formatter)
handler.addFilter(RequestIdFilter())
root_logger.addHandler(handler)
root_logger.setLevel(logging.INFO)

logger = logging.getLogger("nextroute")

class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        req_id = str(uuid.uuid4())
        token = request_id_var.set(req_id)
        
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
        finally:
            request_id_var.reset(token)

