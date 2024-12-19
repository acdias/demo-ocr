# Use an official Python runtime as a parent image
FROM --platform=linux/amd64 python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install poppler-utils and other dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    poppler-utils && \
    rm -rf /var/lib/apt/lists/*  # Clean up to reduce image size

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable to disable buffering
ENV PYTHONUNBUFFERED 1

# Run the Flask application
CMD ["cd", "src", "&&", "gunicorn", "-w", "1", "-b", "0.0.0.0:5000", "--chdir", "/app", "service:app" ]
