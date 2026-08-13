FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for cryptography, psycopg, etc.
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port (Render uses $PORT dynamically, but default to 8000)
EXPOSE 8000

# Apply reviewed migrations, seed local starter content if empty, then start the application.
CMD sh -c "alembic upgrade head && python -m app.db.init_db && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"
