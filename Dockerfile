FROM ubuntu:latest
MAINTAINER Radionomics "radionomics@gmail.com"

RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential libglib2.0-0 libsm6 libxext6 libxrender-dev
RUN apt-get install -y ttf-dejavu

RUN mkdir /var/www
RUN mkdir /var/www/temp_uploads

VOLUME /var/www/temp_uploads /var/lib/docker/volumes/radionomics/data

COPY ./FlaskApp app/FlaskApp
COPY ./runserver.py app
COPY ./requirements.txt app

WORKDIR /app

RUN pip install -r requirements.txt
