#FROM python:alpine3.7
FROM ubuntu:bionic

RUN apt-get update
RUN apt-get install python3 python3-pip -y
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --upgrade setuptools

COPY . ./webapp
COPY helpers/ /webapp/helpers/
RUN pip3 install -r /webapp/app/requirements.txt
EXPOSE 5000
# RUN python3 /webapp/app/app.py
WORKDIR /webapp/app/
ENTRYPOINT [ "python3","app.py" ]
