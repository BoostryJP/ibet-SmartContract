FROM python:3.8-alpine3.15

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
      # use Solidity compiler and AWS CLI
      z3 \
      # use deploy.sh
      jq \
      expect

# use glibc instead of musl-dev
# NOTE: This is because if it is musl-dev, a DynamicLinkError will occur in Solidity compiler.
RUN wget -q -O /etc/apk/keys/sgerrand.rsa.pub https://alpine-pkgs.sgerrand.com/sgerrand.rsa.pub \
 && wget https://github.com/sgerrand/alpine-pkg-glibc/releases/download/2.33-r0/glibc-2.33-r0.apk \
 && apk add glibc-2.33-r0.apk \
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
USER apl
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip setuptools \
 && pip install -r /app/requirements.txt \
 && rm -f /app/requirements.txt

# app deploy
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

# tests deploy
COPY --chown=apl:apl qa.sh /app/ibet-SmartContract/
RUN mkdir -p /app/ibet-SmartContract/tests/
COPY --chown=apl:apl tests/ /app/ibet-SmartContract/tests/
RUN find /app/ibet-SmartContract/ -type d -name __pycache__ | xargs rm -fr

CMD /app/ibet-SmartContract/qa.sh