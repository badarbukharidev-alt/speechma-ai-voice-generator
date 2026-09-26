# Use lightweight Python 3.11/3.12 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=7860

# Working directory
WORKDIR /app

# Install standard Python dependencies (Pillow, FastAPI, Uvicorn, Requests)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Expose server port
EXPOSE 7860

# Start Speechma Studio server
CMD ["python", "run.py", "--host", "0.0.0.0", "--port", "7860", "--no-browser"]
