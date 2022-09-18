# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.205.2/containers/debian/.devcontainer/base.Dockerfile

# [Choice] Debian version (use bullseye or stretch on local arm64/Apple Silicon): bullseye, buster, stretch
ARG VARIANT="buster"
FROM mcr.microsoft.com/vscode/devcontainers/base:0-${VARIANT}

# https://stackoverflow.com/a/56748289
ARG VARIANT

# setup custom apt repository
RUN mkdir -p /usr/local/share/keyrings && gpg --list-keys \
    && gpg --no-default-keyring --keyring /usr/local/share/keyrings/skywrangler-archive-keyring.gpg \
    --keyserver keyserver.ubuntu.com --recv-keys B9B2C01AE12272D7 \
    && echo "deb [signed-by=/usr/local/share/keyrings/skywrangler-archive-keyring.gpg] http://archive.ablerobots.com/skywrangler $VARIANT main" > /etc/apt/sources.list.d/skywrangler.list

# install depedencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends dbus avahi-daemon \
    python3-aiohttp python3-aiohttp-sse python3-dbus-next python3-mavsdk python3-sdnotify \
    black flake8 \
    devscripts debhelper dh-python git-buildpackage dput lintian bash-completion

COPY devscripts.conf /etc/
COPY dput.cf /etc/
COPY git-to-deb.sh /etc/profile.d/
COPY mavsdk-server /etc/init.d/
COPY mock-logind /usr/local/sbin/
COPY org.freedesktop.login1.conf /etc/dbus-1/system.d/
COPY org.freedesktop.login1.service /usr/local/share/dbus-1/system-services/
