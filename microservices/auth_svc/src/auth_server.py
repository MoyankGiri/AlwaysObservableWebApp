from base64 import decode, encode
from email.policy import default
from json import dumps
import logging
from datetime import date, datetime, timedelta

import bcrypt

from concurrent import futures
import grpc

import user_pb2
import user_pb2_grpc as user_grpc

import pymongo
from pymongo.collection import ReturnDocument
from bson.objectid import ObjectId

import jwt
from cryptography.hazmat.primitives import serialization
import os
key = "secret"

import sys
DOCKER = False

if DOCKER:
    sys.path.insert(1,'/webapp/helpers')
else:
    sys.path.insert(1,'/home/chandradhar/Projects/CTY/AlwaysObservableWebApp/helpers')

from error_middlewear import count_error

import prometheus_client
from py_grpc_prometheus.prometheus_server_interceptor import PromServerInterceptor



class userServiceServicer(user_grpc.userServiceServicer):
    def __init__(self) -> None:
        super().__init__()

        print("Creating connection to mongodb on",os.environ.get('DB') or "mongodb://localhost:27017/")
        self.conn = pymongo.MongoClient(os.environ.get('DB') or "mongodb://localhost:27017/")
        # self.conn = pymongo.MongoClient(port=27017)
        self.db = self.conn["blog_app"]
        self.collection = self.db["users"]
        print("Connection Created!")       

    def createAccount(self,req,ctx):
        

        print("Creating Account for user")
        try:
            username = req.username
            password = req.password.encode('utf-8')
            print(username,password)

            salt = bcrypt.gensalt()
            hashedPassword = bcrypt.hashpw(password,salt)

            user = {'username':username,'password':hashedPassword}
            print(user)

            #search if user already exists
            res = self.collection.find_one({'username':username})
            print(f'Found in db: {res}')
            count_error('POST','createAccount','Account Exists')
            if res:
                temp = user_pb2.isSuccess(
                    success=False,
                    msg="Account already exists in database,please login...",
                    userID = res['username']
                )
                print("User Found in mongo!")
                print(temp)
                return user_pb2.isSuccess(
                    success=False,
                    msg="Account already exists in database,please login...",
                    userID=res['username']
                )
            else:
                print("New user!!!")
                #create account for user and insert into database
                rec_id = self.collection.insert_one(user)
                if rec_id:
                    return user_pb2.isSuccess(
                        success=1,
                        msg = "Account created successfully,please login..."
                    )
                else:
                    return user_pb2.isSuccess(
                        success=0,
                        msg = "Unable to create account into db :(, retry.."
                    )
        except Exception as e:
            print(e)
            count_error('POST','create_Account','password decrypting error')
            return user_pb2.isSuccess(
                success=0,
                msg = f'internal server error'
            )

    def login(self,req,ctx):
        
        username = req.username
        password = req.password.encode('utf-8')

        row = self.collection.find_one({'username':username})

        if not row:
            #create account
            count_error('POST','login','incorrect username or password')
            return user_pb2.session(
                success = 0,
                msg = "no account in db,redirecting to signup page...",
                token='',
                timeLimit=''
            )
        else:
            #username found in db,check if password matches
            print(row)
            if bcrypt.checkpw(password,row['password']):
                #generate json web token
                jwt_expiry_time = dumps(datetime.utcnow()+timedelta(minutes=30),indent=4,sort_keys=True,default=str)
                payload = {'username':username,'expiry':jwt_expiry_time}
                token = jwt.encode(payload,key,algorithm='HS256')
                print(f'Encoded {token}')
                
                try:
                    decoded = jwt.decode(token, key, algorithms=['HS256', ])
                    if decoded:
                        print("Username and password matched!!!!")
                        return user_pb2.session(
                            success = 1,
                            msg = "User found and password matched!",
                            token=token,
                            timeLimit = jwt_expiry_time,
                        )
                    else:
                        raise Exception("Faield to decode :(")
                except Exception as e:
                    print("Failed while decoding!!")
                    print(e)
                    count_error('POST','login','jwt decoding error')
                    print("************ERROR COUNTED*****************")
                    return user_pb2.session(
                        success = 0,
                        msg = "Invalid username or password!Try again!",
                        token='',
                        timeLimit='',
                    )
    
    def auth(self,req,ctx):
        token = req.token
        if not token:
            return user_pb2.isSuccess(success=0,msg="Not authorized",userID="")  
        try:
            decoded = jwt.decode(token, key, algorithms=['HS256',])
            print(f"Decoded: {decoded}")
            if decoded:
                print("Successful!!")
                return user_pb2.isSuccess(success=1,msg="Successfull authorization",userID=str(decoded['username']))
            else:
                raise Exception("Failed to decode :(")
        except Exception as e:
            print(e)
            count_error('POST','auth_token','autheorization token generation error')
            return user_pb2.isSuccess(success=0,msg="Unable to authorized",userID="") 

def serve():

    #grpc interceptor
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10),interceptors=(PromServerInterceptor(),))

    user_grpc.add_userServiceServicer_to_server(
        userServiceServicer(),server
    )
    prometheus_client.start_http_server(7299) 

    server.add_insecure_port('[::]:50056')
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    logging.basicConfig()
    serve()

