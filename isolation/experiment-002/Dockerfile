FROM debian:bookworm-slim@sha256:6bd27d44e6c32a66bbd72d7cb2b76a8ae3497ec2e5274a81abd1b37f6013fa1f

ARG DEVIN_VERSION=3000.10.21

ENV DEBIAN_FRONTEND=noninteractive \
    HOME=/root \
    PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
    XDG_CONFIG_HOME=/run/devin-config \
    XDG_DATA_HOME=/run/devin-data

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        bash \
        ca-certificates \
        curl \
        git \
        openssh-client \
        python3 \
        python3-venv \
        ripgrep \
        tar \
    && rm -rf /var/lib/apt/lists/*

# Install the pinned aarch64-unknown-linux bundle directly. The official
# setup.sh ends by launching the interactive login wizard, which is not
# appropriate during an unauthenticated image build; this reproduces its
# manifest selection and SHA-256 verification without running that wizard.
RUN set -eu \
    && curl -fsSL "https://static.devin.ai/cli/${DEVIN_VERSION}/manifest.json" -o /tmp/devin-manifest.json \
    && BUNDLE_URL="$(python3 -c 'import json; print(json.load(open("/tmp/devin-manifest.json"))["platforms"]["aarch64-unknown-linux"]["url"])')" \
    && EXPECTED_SHA256="$(python3 -c 'import json; print(json.load(open("/tmp/devin-manifest.json"))["platforms"]["aarch64-unknown-linux"]["sha256"])')" \
    && curl -fsSL "$BUNDLE_URL" -o /tmp/devin.tar.gz \
    && echo "$EXPECTED_SHA256  /tmp/devin.tar.gz" | sha256sum -c - \
    && mkdir -p "/opt/devin/cli/_versions/${DEVIN_VERSION}" /usr/local/bin \
    && tar xzf /tmp/devin.tar.gz -C "/opt/devin/cli/_versions/${DEVIN_VERSION}" \
    && ln -s "${DEVIN_VERSION}" /opt/devin/cli/_versions/current \
    && ln -s "/opt/devin/cli/_versions/current/bin/devin" /usr/local/bin/devin \
    && rm -f /tmp/devin-manifest.json /tmp/devin.tar.gz \
    && mkdir -p /workspace /artifacts

WORKDIR /workspace

ENTRYPOINT ["/usr/local/bin/devin"]
