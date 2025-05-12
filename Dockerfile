# Base image with Python 3.11
FROM python:3.11-slim

# Install required system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    libnss3 \
    libatk-bridge2.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libxshmfence1 \
    libgtk-3-0 \
    libx11-xcb1 \
    libnss3-tools \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy only requirement-relevant files first to cache layers
COPY pyproject.toml poetry.lock* requirements.txt* ./

# Install pip requirements
RUN pip install --upgrade pip && \
    pip install playwright python-telegram-bot && \
    playwright install --with-deps

# Copy the rest of the code
COPY . .

# Expose environment variables at runtime
ENV TELEGRAM_TOKEN=""
ENV TELEGRAM_CHAT_IDS=""
ENV CHECK_INTERVAL_MINUTES=1

# Run script
CMD ["python", "main.py"]
