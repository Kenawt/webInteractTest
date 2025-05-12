FROM python:3.11-slim

# Install system dependencies for Playwright to run headless Chromium
RUN apt-get update && apt-get install -y \
    libnss3 libxss1 libasound2 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
    libxcomposite1 libxdamage1 libxrandr2 libgbm1 libgtk-3-0 libxkbcommon0 \
    libx11-xcb1 ca-certificates fonts-liberation libappindicator3-1 wget \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN pip install playwright && playwright install --with-deps

# Add your app
COPY main.py .

CMD ["python", "main.py"]
