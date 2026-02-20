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

# Create non-root user and group
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Change ownership of the application directory to the non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Run the server
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "5000"]
