# syntax=docker/dockerfile:1

ARG PY383_IMAGE=python:3.8.3-slim-buster@sha256:47322f8e4b1f0a9a7fbe208f3f5bf51116d69d43314e983c1c1963a5c7873aaa
ARG PY381_IMAGE=python:3.8.1-slim-buster@sha256:ffae7d875975e38d38378ce65d10ab62c2156eb198e2e798664ec6c793015c03
ARG PY370_IMAGE=python:3.7.0-slim-stretch@sha256:749bd3e256151de11e3e9c089d957e05ac1997449c24d8f09b91a5f2f8f2f28b
ARG PY369_IMAGE=python:3.6.9-slim-stretch@sha256:a7b0a171050100296383df09659a434d5c771b77abf94ea0de527768314a8488

FROM ${PY383_IMAGE} AS py383-base
RUN set -eux; \
    sed -i -e 's|http://deb.debian.org/debian|http://archive.debian.org/debian|g' \
           -e 's|http://security.debian.org/debian-security|http://archive.debian.org/debian-security|g' \
           -e '/-updates/d' /etc/apt/sources.list; \
    apt-get -o Acquire::Check-Valid-Until=false update; \
    apt-get install --no-install-recommends -y build-essential; \
    rm -rf /var/lib/apt/lists/*; \
    mkdir -p /opt/e006/runtimes/3.8.3; \
    cp -a /usr/local/. /opt/e006/runtimes/3.8.3/

FROM py383-base AS py383-k01
COPY requirements-k01.txt /tmp/requirements-k01.txt
COPY requirements-test-py38.txt /tmp/requirements-test-py38.txt
RUN set -eux; \
    /opt/e006/runtimes/3.8.3/bin/python3.8 -m venv --copies /opt/e006/venvs/py383-k01; \
    /opt/e006/venvs/py383-k01/bin/python -m pip install --no-cache-dir --no-deps \
      -r /tmp/requirements-k01.txt -r /tmp/requirements-test-py38.txt; \
    rm -f /tmp/requirements-k01.txt /tmp/requirements-test-py38.txt

FROM py383-base AS py383-k03
COPY requirements-k03.txt /tmp/requirements-k03.txt
COPY requirements-test-py38.txt /tmp/requirements-test-py38.txt
RUN set -eux; \
    /opt/e006/runtimes/3.8.3/bin/python3.8 -m venv --copies /opt/e006/venvs/py383-k03; \
    /opt/e006/venvs/py383-k03/bin/python -m pip install --no-cache-dir --no-deps \
      -r /tmp/requirements-k03.txt -r /tmp/requirements-test-py38.txt; \
    rm -f /tmp/requirements-k03.txt /tmp/requirements-test-py38.txt

FROM py383-base AS py383-h
COPY requirements-h.txt /tmp/requirements-h.txt
RUN set -eux; \
    /opt/e006/runtimes/3.8.3/bin/python3.8 -m venv --copies /opt/e006/venvs/py383-h; \
    /opt/e006/venvs/py383-h/bin/python -m pip install --no-cache-dir --no-deps \
      -r /tmp/requirements-h.txt; \
    rm -f /tmp/requirements-h.txt

FROM ${PY381_IMAGE} AS py381-base
RUN set -eux; \
    mkdir -p /opt/e006/runtimes/3.8.1; \
    cp -a /usr/local/. /opt/e006/runtimes/3.8.1/

FROM py381-base AS py381-k02
COPY requirements-k02.txt /tmp/requirements-k02.txt
RUN set -eux; \
    /opt/e006/runtimes/3.8.1/bin/python3.8 -m venv --copies /opt/e006/venvs/py381-k02; \
    /opt/e006/venvs/py381-k02/bin/python -m pip install --no-cache-dir --no-deps \
      -r /tmp/requirements-k02.txt; \
    rm -f /tmp/requirements-k02.txt

FROM ${PY370_IMAGE} AS py370-base
RUN set -eux; \
    sed -i -e 's|http://deb.debian.org/debian|http://archive.debian.org/debian|g' \
           -e 's|http://security.debian.org/debian-security|http://archive.debian.org/debian-security|g' \
           -e '/-updates/d' /etc/apt/sources.list; \
    apt-get -o Acquire::Check-Valid-Until=false update; \
    apt-get -o Acquire::AllowInsecureRepositories=true install --allow-unauthenticated \
      --no-install-recommends -y build-essential; \
    rm -rf /var/lib/apt/lists/*; \
    mkdir -p /opt/e006/runtimes/3.7.0; \
    cp -a /usr/local/. /opt/e006/runtimes/3.7.0/

FROM py370-base AS py370-k04
COPY requirements-k04.txt /tmp/requirements-k04.txt
RUN set -eux; \
    /opt/e006/runtimes/3.7.0/bin/python3.7 -m venv --copies /opt/e006/venvs/py370-k04; \
    /opt/e006/venvs/py370-k04/bin/python -m pip install --no-cache-dir --no-deps \
      -r /tmp/requirements-k04.txt; \
    rm -f /tmp/requirements-k04.txt

FROM ${PY369_IMAGE} AS py369-base
RUN set -eux; \
    sed -i -e 's|http://deb.debian.org/debian|http://archive.debian.org/debian|g' \
           -e 's|http://security.debian.org/debian-security|http://archive.debian.org/debian-security|g' \
           -e '/-updates/d' /etc/apt/sources.list; \
    apt-get -o Acquire::Check-Valid-Until=false update; \
    apt-get -o Acquire::AllowInsecureRepositories=true install --allow-unauthenticated \
      --no-install-recommends -y build-essential; \
    rm -rf /var/lib/apt/lists/*; \
    mkdir -p /opt/e006/runtimes/3.6.9; \
    cp -a /usr/local/. /opt/e006/runtimes/3.6.9/

FROM py369-base AS py369-k05
COPY requirements-k05.txt /tmp/requirements-k05.txt
RUN set -eux; \
    /opt/e006/runtimes/3.6.9/bin/python3.6 -m venv --copies /opt/e006/venvs/py369-k05; \
    /opt/e006/venvs/py369-k05/bin/python -m pip install --no-cache-dir --no-deps \
      -r /tmp/requirements-k05.txt; \
    rm -f /tmp/requirements-k05.txt

FROM devin-e002:3000.10.21@sha256:bb045374bc655c185cced99a6cb769a6695c88527fb432456eb8e0d6dd0e4bb6

ARG BUILD_DATE=unknown
LABEL org.opencontainers.image.title="Devin E006 runtime" \
      org.opencontainers.image.description="Pinned multi-runtime dependency layer for frozen Experiment 006" \
      org.opencontainers.image.created="$BUILD_DATE" \
      org.opencontainers.image.base.name="devin-e002:3000.10.21" \
      org.opencontainers.image.base.digest="sha256:bb045374bc655c185cced99a6cb769a6695c88527fb432456eb8e0d6dd0e4bb6"

COPY runtime-lock.json /opt/e006/runtime-lock.json
COPY --from=py383-h /opt/e006/runtimes/3.8.3 /opt/e006/runtimes/3.8.3
COPY --from=py383-h /opt/e006/venvs/py383-h /opt/e006/venvs/py383-h
COPY --from=py383-k01 /opt/e006/venvs/py383-k01 /opt/e006/venvs/py383-k01
COPY --from=py383-k03 /opt/e006/venvs/py383-k03 /opt/e006/venvs/py383-k03
COPY --from=py381-base /opt/e006/runtimes/3.8.1 /opt/e006/runtimes/3.8.1
COPY --from=py381-k02 /opt/e006/venvs/py381-k02 /opt/e006/venvs/py381-k02
COPY --from=py370-base /opt/e006/runtimes/3.7.0 /opt/e006/runtimes/3.7.0
COPY --from=py370-k04 /opt/e006/venvs/py370-k04 /opt/e006/venvs/py370-k04
COPY --from=py369-base /opt/e006/runtimes/3.6.9 /opt/e006/runtimes/3.6.9
COPY --from=py369-k05 /opt/e006/venvs/py369-k05 /opt/e006/venvs/py369-k05

RUN mkdir -p /opt/e006/compat
COPY --from=py383-base /usr/lib/aarch64-linux-gnu/libffi.so.6.0.4 /opt/e006/compat/libffi.so.6.0.4
RUN ln -s libffi.so.6.0.4 /opt/e006/compat/libffi.so.6

ENV E006_RUNTIME_ROOT=/opt/e006
