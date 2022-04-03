from base64 import encode
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
key = "secret"
class userServiceServicer(user_grpc.userServiceServicer):
    def makeConnection(self):
        print("Creating connection to mongodb....")
        self.conn = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.conn["users"]
        self.collection = self.db["posts"]

    def createAccount(self,req,ctx):
        self.makeConnection()

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
            if res:
                return user_pb2.isSuccess(
                    success=0,
                    msg="User already exists in database,please login..."
                )
            else:
                print("New user!!!")
                #create account for user and insert into database
                rec_id = self.collection.insert_one(user)
                if rec_id:
                    return user_pb2.isSuccess(
                        success=1,
                        msg = "Inserted user into db!"
                    )
                else:
                    return user_pb2.isSuccess(
                        success=0,
                        msg = "Unable to insert into db :(, retry.."
                    )
        except Exception as e:
            print(e)
            return user_pb2.isSuccess(
                success=0,
                msg = f'internal server error'
            )

    def login(self,req,ctx):
        self.makeConnection()
        username = req.username
        password = req.password.encode('utf-8')

        row = self.collection.find_one({'username':username})

        if not row:
            #create account
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
                        return user_pb2.session(
                            success = 1,
                            msg = "User found and password matched!",
                            token=token,
                            timeLimit = jwt_expiry_time
                        )
                except Exception as e:
                    print(e)
                    return user_pb2.session(
                        success = 0,
                        msg = "Invalid username or password!Try again!",
                        token='',
                        timeLimit=''
                    )
    
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_grpc.add_userServiceServicer_to_server(
        userServiceServicer(),server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    logging.basicConfig()
    serve()

