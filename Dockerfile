FROM python:3.10.7
RUN mkdir /app
ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt
COPY . .
CMD python TelegramBot.py