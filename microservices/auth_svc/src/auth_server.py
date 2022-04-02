import logging
from datetime import date

import bcrypt

from concurrent import futures
import grpc

import user_pb2
import user_pb2_grpc as user_grpc

import pymongo
from pymongo.collection import ReturnDocument
from bson.objectid import ObjectId

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
        username = req.username
        password = req.password.encode('utf-8')

        row = self.collection.find_one({'username':username})

        if not row:
            #create account
            return user_pb2.isSuccess(
                success = 0,
                msg = "no account in db,redirecting to signup page..."
            )
        else:
            #username found in db,check if password matches
            print(row)
            if bcrypt.checkpw(password,row['password']):
                return user_pb2.isSuccess(
                    success = 1,
                    msg = "User found and password matched!"
                )
            else:
                return user_pb2.isSuccess(
                    success = 0,
                    msg = "Invalid username or password!Try again!"
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

