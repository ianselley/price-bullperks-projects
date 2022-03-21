FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9-slim

RUN mkdir app
WORKDIR /app

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY creds.json .
COPY app .