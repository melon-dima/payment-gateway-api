FROM python:3.11-slim

WORKDIR /app

# Устанавливаем uv для быстрой установки зависимостей
RUN pip install uv

# Копируем pyproject.toml и устанавливаем зависимости
COPY pyproject.toml .
RUN uv pip install --system .

# Копируем приложение
COPY . .

CMD ["python", "-m", "app.main"]