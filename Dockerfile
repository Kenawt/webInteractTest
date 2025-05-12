FROM python:3.11-slim

WORKDIR /app

# Install OS dependencies for Playwright
RUN apt-get update && apt-get install -y wget gnupg curl \
    libnss3 libatk-bridge2.0-0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 \
    libasound2 libxshmfence1 libgtk-3-0 libx11-xcb1 ca-certificates \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and browser binaries
RUN pip install playwright && playwright install --with-deps

# Copy your code
COPY . .

ENV TELEGRAM_TOKEN=""
ENV TELEGRAM_CHAT_IDS=""
ENV CHECK_INTERVAL_MINUTES=1

CMD ["python", "main.py"]
