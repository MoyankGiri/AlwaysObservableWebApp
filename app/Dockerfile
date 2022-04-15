#FROM python:alpine3.7
FROM ubuntu:bionic

RUN apt-get update
RUN apt-get install python3 python3-pip -y
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --upgrade setuptools

ENV STATIC_URL ./templates
ENV STATIC_PATH ./templates
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

COPY app/ /app/
EXPOSE 5000
WORKDIR /app
RUN ls
RUN pip3 install -r /app/requirements.txt
#ENTRYPOINT FLASK_APP=/app/app flask run --host=0.0.0.0
ENTRYPOINT [ "python3","app/app.py" ]