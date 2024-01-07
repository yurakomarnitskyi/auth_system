FROM python:latest
RUN apt-get update && apt-get install -y supervisor && apt-get install cron -y

COPY . /usr/src/auth_system

WORKDIR /usr/src/auth_system

ADD crontab /etc/cron.d/my-cron-file
RUN crontab /etc/cron.d/my-cron-file

COPY requirements.txt ./
RUN pip install -r requirements.txt
