FROM python:3.13-slim

WORKDIR /app

# uv installation
RUN pip install uv

# Copy the assistant service source code into the image
COPY . .

# Install dependencies with uv
RUN uv sync --no-dev

# Expose the assistant's FastAPI port
EXPOSE 8005

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8005"]