FROM python:3-alpine

COPY requirements.txt /
RUN pip3 install -r requirements.txt

WORKDIR /app
VOLUME /data

ENV DATABASE_SQLITE=/data/db.sqlite
ENV DATA_JSON=/app/data.json

COPY logger.py /app
COPY persistence /app/persistence
COPY bot.py /app
COPY data.json /app/data.json

ENTRYPOINT ["python3", "bot.py"]
