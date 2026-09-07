FROM node:24-alpine

# gcc stays in the image: entrypoint.sh bakes $FLAG into /readflag at boot
RUN apk add --no-cache shadow socat gcc libc-dev && \
    groupadd -g 10000 jail && \
    useradd --create-home -u 10000 -g 10000 jail && \
    apk del shadow && \
    touch /readflag && \
    chown 10000:10000 /readflag && \
    chmod 0311 /readflag

WORKDIR /home/jail/

COPY package.json package-lock.json /home/jail/

RUN npm install

COPY chal.js jail.js /home/jail/
COPY --chmod=444 readflag.c /src/readflag.c
COPY --chmod=555 entrypoint.sh /entrypoint.sh

USER jail

ENV NODE_ENV production

ENTRYPOINT ["/entrypoint.sh"]
