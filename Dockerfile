# Use a lightweight Python base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the application code into the container
COPY . /app

# Install the required Python packages
RUN pip install --no-cache-dir flask psycopg2 boto3

# Expose the port the app will run on
EXPOSE 5000

# Command to run the app
CMD ["python", "app.py"]

