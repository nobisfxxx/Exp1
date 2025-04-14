# Use the official Python 3.12 slim image as a base
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system dependencies for building Cython extensions and Pillow
RUN apt-get update && apt-get install -y \
    gcc \
    libjpeg-dev \
    zlib1g-dev \
    build-essential \
    && apt-get clean

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Install Cython extension
RUN python setup.py install

# Run the bot script when the container starts
CMD ["python", "bot.py"]
