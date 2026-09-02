FROM python:3.12-alpine

RUN apk add --no-cache git tar

RUN pip install --no-cache-dir flask gunicorn

WORKDIR /app

COPY app.py .
COPY templates/ templates/
COPY flag.txt /app

RUN mkdir -p /app/repos \
    && adduser -D appuser \
    && chown -R appuser /app

USER appuser

EXPOSE 80

CMD ["gunicorn", "-b", "0.0.0.0:80", "app:app"]
