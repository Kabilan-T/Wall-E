FROM python:3.6.8

RUN mkdir /app

ADD . /app

WORKDIR /app

RUN pip install -r requirements.txt

COPY . .

CMD python TelegramBot.py