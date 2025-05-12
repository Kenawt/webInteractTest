FROM python:3.11-slim

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget curl gnupg libnss3 libxss1 libasound2 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
    libxcomposite1 libxdamage1 libxrandr2 libgbm1 libgtk-3-0 libxkbcommon0 \
    libx11-xcb1 libpangocairo-1.0-0 libpangoft2-1.0-0 ca-certificates fonts-liberation \
    libappindicator3-1 libu2f-udev libvulkan1 unzip xvfb lsb-release gnupg2 \
    && rm -rf /var/lib/apt/lists/*

# Install Python and Playwright dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers manually
RUN playwright install --with-deps

# Add source code
COPY main.py .

# Health check to prevent silent failure
HEALTHCHECK CMD curl --fail http://localhost:8080 || exit 1

CMD ["python", "main.py"]
