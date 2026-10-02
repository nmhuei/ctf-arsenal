FROM python:3-alpine

COPY ./requirements.txt requirements.txt
RUN pip3 install -r requirements.txt && rm requirements.txt

WORKDIR /app

RUN addgroup -S app && adduser -S -H -G app app
USER app

CMD gunicorn -c /app/gunicorn.conf.py
