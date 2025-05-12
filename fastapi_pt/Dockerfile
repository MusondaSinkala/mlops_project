# Use a slim base Python image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Copy your FastAPI app
COPY app.py .

# Install required Python packages
RUN pip install fastapi uvicorn pandas scikit-learn mlflow

# Expose FastAPI port
EXPOSE 8001

# Run the FastAPI server
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]