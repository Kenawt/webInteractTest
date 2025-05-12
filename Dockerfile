FROM mcr.microsoft.com/playwright/python:v1.52.0-jammy

WORKDIR /app

COPY main.py .

RUN python -m pip install python-telegram-bot==20.6

CMD ["python", "main.py"]
