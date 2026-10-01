FROM python:3.10-slim

WORKDIR /app

COPY requirements-fetcher.txt .
RUN pip install --no-cache-dir -r requirements-fetcher.txt 
COPY . .

CMD ["python","fetcher.py"]