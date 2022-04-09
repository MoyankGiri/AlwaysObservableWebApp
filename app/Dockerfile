# change directory to app to use this
FROM python:alpine3.7
ENV STATIC_URL ./templates
ENV STATIC_PATH ./templates
COPY . /tmp
WORKDIR /tmp
EXPOSE 5000
RUN pip install -r /tmp/requirements.txt
ENTRYPOINT FLASK_APP=app flask run --host=0.0.0.0