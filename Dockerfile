FROM python:3-slim

COPY requirements.txt /
RUN pip3 install -r requirements.txt

COPY logger.py /
COPY LaVidaModerna/data.json data.json
COPY bot.py /

ENTRYPOINT ["python3", "/bot.py"]
