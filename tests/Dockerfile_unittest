FROM ghcr.io/foundry-rs/foundry:latest AS foundry

FROM python:3.13-slim

ENV UV_VERSION=0.10.12
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_INSTALL_DIR="/usr/local/bin"
ENV UV_PROJECT_ENVIRONMENT="/home/apl/.venv"

# Make application directory
RUN mkdir -p /app/ibet-SmartContract/
WORKDIR /app/ibet-SmartContract/

# Install packages
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    autoconf \
    automake \
    awscli \
    bash \
    build-essential \
    expect \
    git \
    jq \
    libffi-dev \
    libssl-dev \
    libtool \
    make \
    pkg-config \
    sudo \
    wget \
    z3 \
 && rm -rf /var/lib/apt/lists/*

# add apl user/group
RUN groupadd -g 1000 apl \
 && useradd -g apl -m -s /bin/bash -u 1000 apl \
 && echo 'apl ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers \
 && chown -R apl:apl /app \
 && echo 'export LANG=ja_JP.utf8' >> ~apl/.profile

# install uv
ADD https://astral.sh/uv/$UV_VERSION/install.sh /uv-installer.sh
RUN INSTALLER_NO_MODIFY_PATH=1 sh /uv-installer.sh && rm /uv-installer.sh
COPY --from=foundry /usr/local/bin/anvil /usr/local/bin/anvil
RUN echo 'if [ -f ~/.ashrc ]; then' >> ~apl/.profile \
 && echo '    . ~/.ashrc' >> ~apl/.profile \
 && echo 'fi' >> ~apl/.profile \
 && echo '. $HOME/.venv/bin/activate' >> ~apl/.ashrc

# prepare venv
USER apl
RUN mkdir /home/apl/.venv

# install python packages
COPY pyproject.toml /app/ibet-SmartContract/pyproject.toml
COPY uv.lock /app/ibet-SmartContract/uv.lock
RUN cd /app/ibet-SmartContract \
 && uv venv $UV_PROJECT_ENVIRONMENT \
 && uv sync --frozen --no-install-project \
 && rm -f /app/ibet-SmartContract/pyproject.toml \
 && rm -f /app/ibet-SmartContract/uv.lock

# deploy app
COPY --chown=apl:apl LICENSE /app/ibet-SmartContract/
RUN mkdir -p /app/ibet-SmartContract/tools/
COPY --chown=apl:apl tools/ /app/ibet-SmartContract/tools/
COPY --chown=apl:apl brownie-config.yaml /app/ibet-SmartContract/
RUN mkdir -p /app/ibet-SmartContract/data/
COPY --chown=apl:apl data/ /app/ibet-SmartContract/data/
RUN . ~apl/.profile \
 && cd /app/ibet-SmartContract/ \
 && brownie networks import data/networks.yml
RUN mkdir -p /app/ibet-SmartContract/scripts/
COPY --chown=apl:apl scripts/ /app/ibet-SmartContract/scripts/
RUN mkdir -p /app/ibet-SmartContract/interfaces/
COPY --chown=apl:apl interfaces/ /app/ibet-SmartContract/interfaces/
RUN mkdir -p /app/ibet-SmartContract/contracts/
COPY --chown=apl:apl contracts/ /app/ibet-SmartContract/contracts/
RUN find /app/ibet-SmartContract/ -type d -name __pycache__ | xargs rm -fr \
 && chmod -R 755 /app/ibet-SmartContract/

# deploy test modules
COPY --chown=apl:apl qa.sh /app/ibet-SmartContract/
RUN mkdir -p /app/ibet-SmartContract/tests/
COPY --chown=apl:apl tests/ /app/ibet-SmartContract/tests/
RUN find /app/ibet-SmartContract/ -type d -name __pycache__ | xargs rm -fr

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/ibet-SmartContract

CMD ["sh", "/app/ibet-SmartContract/qa.sh"]