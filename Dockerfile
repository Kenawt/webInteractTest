FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy

# Copy your app code
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py ./

CMD ["python", "main.py"]
