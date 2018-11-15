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
            libyaml-cpp-dev && \
    apt-get install -y software-properties-common && \
    add-apt-repository -y ppa:ethereum/ethereum && \
    apt-get update -y && \
    apt-get install -y solc=0.4.24-0ubuntu1~xenial

# GO
ENV GOREL go1.7.3.linux-amd64.tar.gz
ENV PATH $PATH:/usr/local/go/bin
RUN wget -q https://storage.googleapis.com/golang/$GOREL && \
    tar xfz $GOREL && \
    mv go /usr/local/go && \
    rm -f $GOREL

# Quorum
RUN git clone https://github.com/jpmorganchase/quorum.git && \
    cd quorum && \
    make all && \
    cp build/bin/geth /usr/local/bin && \
    cp build/bin/bootnode /usr/local/bin && \
    cd .. && \
    rm -rf quorum

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
 && pyenv install 3.6.2 \
 && pyenv global 3.6.2 \
 && pip install --upgrade pip

# requirements
COPY requirements.txt /app/requirements.txt
RUN . ~/.bash_profile \
 && pip install -r /app/requirements.txt

# app
USER root
COPY . /app/tmr-sc/
RUN chown -R apl:apl /app/tmr-sc && \
    chmod 755 /app/tmr-sc
USER apl
COPY qa.sh /app/tmr-sc/

CMD /app/tmr-sc/qa.sh
