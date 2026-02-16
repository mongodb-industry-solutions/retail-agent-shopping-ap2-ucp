# Use official Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -e .

# Expose port
EXPOSE 5000

# Run the server
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "5000"]
