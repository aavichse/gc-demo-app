# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables (optional defaults)
ENV APP_ID="tester"
ENV TARGETS=""
ENV PORT=8000

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN apt update && apt install -y curl 

# Expose the port that the Flask app will run on
EXPOSE $PORT

# Define the command to run the Flask app, using environment variables for PORT
CMD ["python", "app.py"]

