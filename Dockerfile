FROM python:3.10-slim

WORKDIR /root/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements/ requirements/

RUN apt update && \
        apt install -y ffmpeg && \
        apt clean && \
        rm -rf /var/lib/apt/lists/* && \
        pip install --upgrade pip && \
        pip install -r requirements/production.txt && \
        rm -rf requirements/

COPY . .

CMD ["python", "./bot.py"]
