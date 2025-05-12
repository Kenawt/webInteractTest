FROM python:3.11-slim

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget curl gnupg libnss3 libxss1 libasound2 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
    libxcomposite1 libxdamage1 libxrandr2 libgbm1 libgtk-3-0 libxkbcommon0 \
    libx11-xcb1 libpangocairo-1.0-0 libpangoft2-1.0-0 fonts-liberation \
    libappindicator3-1 libu2f-udev libvulkan1 unzip xvfb lsb-release gnupg2 \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright and Telegram bot package
RUN pip install --no-cache-dir playwright python-telegram-bot==20.6

# Install browsers
RUN playwright install --with-deps

WORKDIR /app
COPY main.py .

CMD ["python", "main.py"]
