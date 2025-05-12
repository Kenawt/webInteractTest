FROM mcr.microsoft.com/playwright/python:v1.52.0-jammy

WORKDIR /app

RUN pip install python-telegram-bot==20.6

COPY main.py .

CMD python main.py
