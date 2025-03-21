FROM python:3.11-alpine3.19

ENV UV_VERSION=0.6.5
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_INSTALL_DIR="/usr/local/bin"
ENV UV_PROJECT_ENVIRONMENT="/home/apl/.venv"

# make application directory
RUN mkdir -p /app/ibet-SmartContract/

# install packages
RUN apk update \
    && apk add --no-cache --virtual .build-deps \
    # use Python package installation
    make \
    gcc \
    pkgconfig \
    build-base \
    libressl-dev \
    libffi-dev \
    autoconf \
    automake \
    libtool \
    git \
    # use Solidity compiler
    z3 \
    # AWS CLI
    aws-cli \
    mandoc \
    # use deploy.sh
    jq \
    expect

# use glibc instead of musl-dev
# NOTE: This is because if it is musl-dev, an dynamic link error will occur in Solidity compiler.
RUN wget -q -O /etc/apk/keys/sgerrand.rsa.pub https://alpine-pkgs.sgerrand.com/sgerrand.rsa.pub \
 && wget https://github.com/sgerrand/alpine-pkg-glibc/releases/download/2.33-r0/glibc-2.33-r0.apk \
 && apk add --force-overwrite glibc-2.33-r0.apk \
 && rm -f glibc-2.33-r0.apk
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/lib

# add apl user/group
RUN addgroup -g 1000 apl \
 && adduser -G apl -D -s /bin/bash -u 1000 apl \
 && echo 'apl ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers \
 && chown -R apl:apl /app \
 && echo 'export LANG=ja_JP.utf8' >> ~apl/.profile

# install uv
ADD https://astral.sh/uv/$UV_VERSION/install.sh /uv-installer.sh
RUN INSTALLER_NO_MODIFY_PATH=1 sh /uv-installer.sh && rm /uv-installer.sh
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
 && uv sync --frozen --no-dev --no-install-project \
 && rm -f /app/ibet-SmartContract/pyproject.toml \
 && rm -f /app/ibet-SmartContract/uv.lock

# deploy app
USER apl
COPY --chown=apl:apl LICENSE /app/ibet-SmartContract/
RUN mkdir -p /app/ibet-SmartContract/tools/
COPY --chown=apl:apl tools/ /app/ibet-SmartContract/tools/
COPY --chown=apl:apl brownie-config.yaml /app/ibet-SmartContract/
RUN mkdir -p /app/ibet-SmartContract/data/
COPY --chown=apl:apl data/ /app/ibet-SmartContract/data/
RUN source ~apl/.profile \
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

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/ibet-SmartContract

CMD ["sh"]