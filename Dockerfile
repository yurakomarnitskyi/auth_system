FROM python:latest
RUN apt-get update && apt-get install -y supervisor

COPY . /usr/src/auth_system

WORKDIR /usr/src/auth_system

COPY requirements.txt ./
RUN pip install -r requirements.txt
