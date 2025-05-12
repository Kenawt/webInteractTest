FROM mcr.microsoft.com/playwright/python:v1.52.0-jammy

WORKDIR /app

COPY main.py .

# Install telegram bot into the built-in virtual environment where playwright is installed
RUN /ms-playwright/.venv/bin/pip install python-telegram-bot==20.6

# Use the Python interpreter from the same virtual environment
CMD ["/ms-playwright/.venv/bin/python", "main.py"]
