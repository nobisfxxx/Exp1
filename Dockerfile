# Use the official Python 3.12 slim image as a base
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system dependencies (Pillow requires libjpeg)
RUN apt-get update && apt-get install -y \
    libjpeg-dev \
    zlib1g-dev

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Install Cython (if required)
RUN python setup.py build_ext --inplace

# Run the bot script when the container starts
CMD ["python", "bot.py"]
