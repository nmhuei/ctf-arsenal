FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends nodejs npm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /brain
COPY brain/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch==2.5.1 \
    && pip install --no-cache-dir -r requirements.txt
COPY brain/main.py ./main.py

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --omit=dev
COPY src ./src
COPY public ./public
COPY start.sh /usr/local/bin/no-hot-water-club
RUN chmod +x /usr/local/bin/no-hot-water-club
ENV PORT=3000
EXPOSE 3000
CMD ["no-hot-water-club"]
