FROM python:3.11-slim

WORKDIR /app

# Install uv for fast dependency installation
RUN pip install uv

# Copy pyproject.toml and install dependencies
COPY pyproject.toml .
RUN uv pip install --system .

# Copy application
COPY . .

# Run migrations and start app
CMD ["sh", "-c", "alembic upgrade head && python -m app.main"]