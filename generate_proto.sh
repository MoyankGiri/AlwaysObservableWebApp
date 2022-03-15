#! /bin/sh

rm -f microservices/$1/src/$1_pb2_grpc.py
rm -f microservices/$1/src/$1_pb2.py

python -m grpc_tools.protoc -I=_proto --python_out=. --grpc_python_out=microservices/$1/src _proto/$2.proto

python -m grpc_tools.protoc -I=_proto --python_out=microservices/$1/src _proto/$2.proto