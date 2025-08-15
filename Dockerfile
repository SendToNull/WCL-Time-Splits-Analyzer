# Use an official lightweight Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables for the container
ENV PYTHONUNBUFFERED True  # Prevents python output from being buffered, making logs appear in real-time
ENV APP_HOME /app          # Define the home directory for the application
WORKDIR $APP_HOME          # Set the working directory in the container to /app

# Copy the requirements file into the container first
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the local application code to the container
COPY . .

# Run the web service on container startup using Gunicorn
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app