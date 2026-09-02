FROM lscr.io/linuxserver/webtop:debian-xfce

RUN apt-get update && apt-get install -y --no-install-recommends \
    libqt6widgets6 \
    qt6-qpa-plugins \
    && rm -rf /var/lib/apt/lists/*

COPY --chmod=0755 phantasmoon-gui /usr/local/bin/phantasmoon-gui
COPY robot.s /opt/phantasmoon/robot.s

ENV START_DOCKER=false \
    TITLE=Phantasmoon

EXPOSE 3001
