FROM python:3.10-alpine

RUN mkdir api
WORKDIR /api

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY creds.json .
COPY app .

CMD [ "python", "main.py" ]