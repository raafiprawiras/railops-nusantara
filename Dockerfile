# Base Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy requirements first for Docker layer caching
COPY requirements.txt .

# Install dependencies
RUN pip install --index-url https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser -d /app appuser && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 5000

# Run the application with Gunicorn binding to port 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:create_app()"]
