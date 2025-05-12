FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy app code
COPY app.py .

# Install dependencies
RUN pip install fastapi uvicorn pandas scikit-learn mlflow

# Expose port
EXPOSE 8000

# Run the app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]


