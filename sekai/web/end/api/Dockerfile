FROM python:3.12-slim

RUN groupadd -g 1001 app \
 && useradd -m -s /bin/bash -u 1001 -g 1001 app

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

RUN chown -R root:root /app \
 && chmod -R 555 /app

USER app

EXPOSE 9090

CMD ["flask", "run", "--host=0.0.0.0", "--port=9090"]
