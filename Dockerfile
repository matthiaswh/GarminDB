FROM python:3.8

WORKDIR /opt

RUN apt-get update && apt-get install -y cron zip build-essential git python3 python3-pip
RUN pip install sqlalchemy requests python-dateutil lxml

# Adds host key for github since make setup pulls submodules
RUN mkdir ~/.ssh
RUN ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts

COPY . .
COPY GarminConnectConfig.json.example GarminConnectConfig.json

# This isn't really ideal since Docker can't cache this intermediate step
RUN make deps
