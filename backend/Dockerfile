FROM python:3.13-slim

WORKDIR /app

# uv installation
RUN pip install uv

# Copy the backend code
COPY ./backend/ .

# Install dependencies with uv
RUN uv sync --no-dev

# Expose main FastAPI port and all A2A agent ports
EXPOSE 8000 8001 8002 8003 8004

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]