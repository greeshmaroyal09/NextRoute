import multiprocessing

# Bind to 0.0.0.0 for Docker
bind = "0.0.0.0:8000"

# Uvicorn ASGI worker class
worker_class = "uvicorn.workers.UvicornWorker"

# Dynamically calculate workers based on CPU cores
workers = multiprocessing.cpu_count() * 2 + 1

# Graceful timeout configurations
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
