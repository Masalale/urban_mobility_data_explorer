# Use official Python runtime as base image
FROM python:3.12-slim

# Set working directory in container
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project into container
COPY . .

# Run data cleaning, database creation, and setup in sequence
RUN python scripts/data_cleaning.py && \
    python backend/database/db.py

# Expose port 5000 for Flask
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=backend/app.py
ENV FLASK_ENV=production

# Run the application
CMD ["python", "backend/app.py"]
