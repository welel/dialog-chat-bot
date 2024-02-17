FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN apt update && \
        apt install -y ffmpeg && \
        apt clean && \
        rm -rf /var/lib/apt/lists/* && \
        pip install --upgrade pip && \
        pip install -r requirements.txt

COPY . .

CMD ["python", "./bot.py"]
