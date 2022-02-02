FROM python:3.10-alpine

RUN mkdir telegram_bot
WORKDIR /telegram_bot

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY creds.json .
COPY sheets.py .
COPY main.py .

CMD [ "python", "main.py" ]