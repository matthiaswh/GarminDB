FROM python:3.8

WORKDIR /opt

RUN apt-get update && apt-get install -y cron zip build-essential git python3 python3-pip
RUN pip install sqlalchemy requests python-dateutil lxml

# Adds host key for github since make setup pulls submodules
RUN mkdir ~/.ssh
RUN ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts

COPY . .
RUN mkdir /root/.GarminDb
COPY garmindb/GarminConnectConfig.json.example /root/.GarminDb/GarminConnectConfig.json

# This isn't really ideal since Docker can't cache this intermediate step
RUN make deps
# garmindb (somehow) installs itself in a venv, which doesn't get passed the env vars we send from Docker
# Since we're copying the source anyway, just install editable, which should give what we need.
RUN pip install -e .
