FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY scripts/ scripts/

RUN mkdir -p data/raw data/processed data/analytics

CMD ["python", "scripts/run_bot.py"]
