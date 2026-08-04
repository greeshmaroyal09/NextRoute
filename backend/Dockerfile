FROM python:3.11-slim

# Create non-root user
RUN adduser --system --group appuser

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn uvicorn

# Copy app code
COPY app /app/app
COPY gunicorn.conf.py /app/gunicorn.conf.py

# Switch to non-root user
USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/v1/health/ || exit 1

CMD ["gunicorn", "-c", "gunicorn.conf.py", "app.main:app"]
