FROM python:3.10-slim
LABEL authors="Panfilov Valerian"

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY config/ ./config/

CMD ["python", "src/bot.py"]
