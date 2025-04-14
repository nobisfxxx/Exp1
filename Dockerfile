# Use an official Python runtime as the base image
FROM python:3.12-slim

# Install build dependencies for Cython
RUN apt-get update && apt-get install -y build-essential gcc

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Install Cython and build the Cython extension
RUN python setup.py build_ext --inplace

# Expose a port if you plan to use Flask (optional)
# EXPOSE 5000

# Run your Instagram bot script when the container starts
CMD ["python", "bot.py"]
