FROM mcr.microsoft.com/playwright/python:v1.42.1-jammy

WORKDIR /app

# Install Telegram bot lib
RUN pip install --no-cache-dir python-telegram-bot

# Copy the rest of your code
COPY . .

CMD ["python", "main.py"]
