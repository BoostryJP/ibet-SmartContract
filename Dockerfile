FROM ubuntu:16.04

# make application directory
RUN mkdir -p /app

# add apl user/group
RUN groupadd -g 1000 apl \
 && useradd -g apl -s /bin/bash -u 1000 -p apl apl \
 && echo 'apl ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers \
 && chown -R apl:apl /app

# install packages
RUN apt-get update && \
    apt-get install -y \
            build-essential \
            libleveldb-dev \
            git \
            libdb-dev \
            libsodium-dev \
            libtinfo-dev \
            sysvbanner \
            unzip \
            wget \
            wrk \
            zlib1g-dev \
            ca-certificates \
            curl \
            libbz2-dev \
            libreadline-dev \
            libsqlite3-dev \
            libssl-dev \
            zlib1g-dev \
            libffi-dev \
            python3-dev \
            libpq-dev \
            automake \
            pkg-config \
            libtool \
            libgmp-dev \
            language-pack-ja-base \
            language-pack-ja \
            libyaml-cpp-dev \
            libgcc1 \
            libstdc++6 \
            libz3-dev \
            jq \
            expect

# AWS CLI
RUN wget -q https://awscli.amazonaws.com/awscli-exe-linux-$(arch).zip -O awscliv2.zip && \
    unzip awscliv2.zip && \
    ./aws/install && \
    rm -r aws awscliv2.zip

# pyenv
RUN git clone https://github.com/pyenv/pyenv.git
RUN mkdir -p /home/apl \
 && mv /pyenv /home/apl/.pyenv/ \
 && chown -R apl:apl /home/apl

# install pyenv
USER apl
RUN echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~apl/.bash_profile \
 && echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~apl/.bash_profile \
 && echo 'eval "$(pyenv init -)"' >> ~apl/.bash_profile \
 && echo 'export LANG=ja_JP.utf8' >> ~apl/.bash_profile

# install python & package
RUN . ~/.bash_profile \
 && pyenv install 3.6.10 \
 && pyenv global 3.6.10 \
 && pip install --upgrade pip

# requirements
COPY requirements.txt /app/requirements.txt
RUN . ~/.bash_profile \
 && pip install -r /app/requirements.txt

# app
USER root
COPY . /app/ibet-SmartContract/
RUN chown -R apl:apl /app/ibet-SmartContract && \
    chmod 755 /app/ibet-SmartContract
USER apl
RUN . ~/.bash_profile \
  && cd /app/ibet-SmartContract/ \
  && brownie networks import data/networks.yml
COPY qa.sh /app/ibet-SmartContract/

CMD /app/ibet-SmartContract/qa.sh
