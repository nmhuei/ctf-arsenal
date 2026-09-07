FROM node:24-alpine

# gcc stays in the image: entrypoint.sh bakes $FLAG into /readflag at boot
RUN apk add --no-cache shadow socat gcc libc-dev && \
    useradd --create-home jail && \
    apk del shadow && \
    touch /readflag && \
    chown jail:jail /readflag && \
    chmod 0311 /readflag

WORKDIR /home/jail/

COPY package.json package-lock.json /home/jail/

RUN npm install

COPY . /home/jail/
COPY --chmod=444 readflag.c /src/readflag.c
COPY --chmod=555 entrypoint.sh /entrypoint.sh

USER jail

ENV NODE_ENV production

RUN ["npm", "run", "build"]

ENTRYPOINT ["/entrypoint.sh"]
