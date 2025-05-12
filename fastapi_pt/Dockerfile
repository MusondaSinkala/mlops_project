











FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy app code into the container
COPY app.py .

# Install FastAPI and Uvicorn
RUN pip install --no-cache-dir fastapi uvicorn

# Expose the port FastAPI will run on
EXPOSE 8000

# Run the FastAPI server
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]





