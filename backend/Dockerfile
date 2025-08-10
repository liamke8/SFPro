# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory for the application
WORKDIR /usr/src/app

# Copy the requirements file into a backend subdirectory
COPY ./requirements.txt /usr/src/app/backend/

# Install any needed packages specified in requirements.txt
# We also install playwright's browser dependencies here
RUN pip install --no-cache-dir -r /usr/src/app/backend/requirements.txt && playwright install --with-deps

# Copy the rest of the backend application code into the backend subdirectory
COPY . /usr/src/app/backend/

# Add the app directory to the PYTHONPATH to allow for absolute imports
ENV PYTHONPATH "${PYTHONPATH}:/usr/src/app"

# Make port 8000 available to the world outside this container
EXPOSE 8000
