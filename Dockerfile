# Use official Playwright base image (includes Chromium + deps)
FROM mcr.microsoft.com/playwright/python:v1.43.1-jammy

# Set working directory
WORKDIR /app

# Copy only requirement files first for caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app
COPY . .

# Set env vars here or from Railway's dashboard
ENV TELEGRAM_TOKEN=""
ENV TELEGRAM_CHAT_IDS=""
ENV CHECK_INTERVAL_MINUTES=1

# Default command
CMD ["python", "main.py"]
