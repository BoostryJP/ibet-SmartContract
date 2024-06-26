FROM python:3.11-alpine3.19

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
      # use Solidity compiler and AWS CLI
      z3 \
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

# AWS CLI
RUN wget -q https://awscli.amazonaws.com/awscli-exe-linux-$(arch).zip -O awscliv2.zip \
 && unzip awscliv2.zip \
 && ./aws/install \
 && rm -r aws awscliv2.zip

# add apl user/group
# NOTE: '/bin/bash' was added when 'libtool' installed.
RUN addgroup -g 1000 apl \
 && adduser -G apl -D -s /bin/bash -u 1000 apl \
 && echo 'apl ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers \
 && chown -R apl:apl /app \
 && echo 'export LANG=ja_JP.utf8' >> ~apl/.bash_profile \
 && echo 'export PATH=$PATH:$HOME/.local/bin' >> ~apl/.bash_profile

# Python requirements
RUN python -m pip install poetry==1.7.1 && python -m poetry config virtualenvs.create false
COPY pyproject.toml /app/pyproject.toml
COPY poetry.lock /app/poetry.lock
RUN python -m poetry install --no-root --directory /app/ \
  && rm -f /app/pyproject.toml \
  && rm -f /app/poetry.lock

# app deploy
USER apl
COPY --chown=apl:apl LICENSE /app/ibet-SmartContract/
RUN mkdir -p /app/ibet-SmartContract/tools/
COPY --chown=apl:apl tools/ /app/ibet-SmartContract/tools/
COPY --chown=apl:apl brownie-config.yaml /app/ibet-SmartContract/
RUN mkdir -p /app/ibet-SmartContract/data/
COPY --chown=apl:apl data/ /app/ibet-SmartContract/data/
RUN source ~apl/.bash_profile \
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

CMD sh /app/ibet-SmartContract/scripts/deploy_shared_contract.sh