FROM ubuntu:bionic

RUN apt-get update
RUN apt-get install python3 python3-pip -y
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --upgrade setuptools
COPY _proto/ /_proto/
COPY microservices/ /microservices/
COPY helpers/ /webapp/helpers/

RUN ls
RUN ls /microservices/
RUN ls /microservices/auth_svc/
RUN ls /webapp/helpers/

WORKDIR /microservices/auth_svc/src/
RUN pip install -r ./requirements.txt
RUN python3 -m grpc_tools.protoc -I ../../../_proto --python_out=. --grpc_python_out=. ../../../_proto/user.proto
RUN python3 -m grpc_tools.protoc -I ../../../_proto --python_out=. --grpc_python_out=. ../../../_proto/shared.proto

EXPOSE 50056
CMD [ "python3","auth_server.py" ]