# ── Stage 1: Base Image ──────────────────────────────────
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Create a non-root user for security
RUN adduser --disabled-password --gecos '' gymuser && \
    chown -R gymuser:gymuser /app
USER gymuser

# Expose port
EXPOSE 5000

# Initialize DB and run app
CMD ["python", "-c", "from app import init_db; init_db()"] ; \
    python app.py
# Use shell form so both commands run
ENTRYPOINT ["/bin/sh", "-c", "python -c 'from app import init_db; init_db()' && python app.py"]
