FROM python:3-slim

RUN apt update && apt install --no-cache -y unixodbc-dev libsqlite0-dev libsqliteodbc git

WORKDIR /usr/app

RUN git clone https://github.com/nectostr/VocabularyBot . 

RUN pip3 install -r requirements.txt

CMD ["python3", "bot.py"]

