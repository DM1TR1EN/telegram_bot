# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files from the current directory to the container
COPY . .

# Create directory for mounted files
RUN mkdir -p /app/data

# Command to run the bot
CMD ["python", "main.py"] 