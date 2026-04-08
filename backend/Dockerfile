FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps for common ML/audio/video wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    libgl1 \
    libglib2.0-0 \
  && rm -rf /var/lib/apt/lists/*

# Install Python deps first (better layer caching)
COPY backend_requirements.txt /app/backend_requirements.txt
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy the app source
COPY backend /app/backend
COPY saved_model /app/saved_model
COPY data /app/data

# Render provides $PORT
EXPOSE 10000

CMD ["bash", "-lc", "gunicorn -b 0.0.0.0:${PORT:-10000} backend.app:app --timeout 120"]
