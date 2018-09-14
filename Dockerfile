FROM python:3.6

ENV PYTHONUNBUFFERED 1
ENV HOME /garnet
ENV USER garnet

RUN mkdir $HOME
COPY tools/utils.sh requirements.txt $HOME/
WORKDIR $HOME

RUN apt update \
    && apt-get install -y \
    mysql-client \
    enchant \
    libxmlsec1-dev \
    pkg-config \
    adduser \
    vim \
    && rm -rf /var/lib/apt/lists/* \
    && pip install virtualenv \
    && virtualenv venv \
    && . venv/bin/activate \
    && pip install -r requirements.txt \
    && useradd --home-dir $HOME $USER \
    && chown -R $USER $HOME
