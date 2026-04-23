FROM python:3.11-slim

# Install FFmpeg (required for video processing)
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY bot.py .

# Create downloads directory
RUN mkdir -p /tmp/downloads

# Run the bot
CMD ["python", "-u", "bot.py"]
