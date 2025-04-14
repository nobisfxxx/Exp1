# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install the required dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Install Cython for compiling the .pyx file
RUN apt-get update && apt-get install -y gcc python3-dev
RUN python setup.py build_ext --inplace

# Expose port if necessary (for Flask, etc.)
# EXPOSE 5000

# Run your Instagram bot script when the container starts
CMD ["python", "bot.py"]
