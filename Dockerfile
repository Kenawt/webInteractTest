FROM mcr.microsoft.com/playwright/python:v1.42.1-jammy

WORKDIR /app

# Install Telegram bot library
RUN pip install --no-cache-dir python-telegram-bot

# Copy all files
COPY . .

# Set environment variables (to override in Railway)
ENV TELEGRAM_TOKEN=""
ENV TELEGRAM_CHAT_IDS=""
ENV CHECK_INTERVAL_MINUTES=1

CMD ["python", "main.py"]
