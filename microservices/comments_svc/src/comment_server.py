import logging
from datetime import date, datetime, timedelta

from concurrent import futures
from time import strptime
import grpc

import comments_pb2
import comments_pb2_grpc 

import pymongo
from pymongo.collection import ReturnDocument
from bson.objectid import ObjectId

class commentServiceServicer(comments_pb2_grpc.commentServiceServicer):

    def makeConnection(self):
        self.conn = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.conn["blog"]
        self.collection = self.db["comments"]
    

    def createComment(self,req,ctx):

        self.makeConnection()
        ret = None
        try:
            
            data = {
                "title":req.title,
                "body":req.body,
                "author":req.author,
                "parentPost":req.parentPost,
                "parentComment":req.parentComment,
                "userID":req.userID
            }
            rec_id = self.collection.insert_one(data)
            ret = comments_pb2.commentItem(
                id=f"{rec_id.inserted_id}",
                title=req.title,
                body=req.body,
                author=req.author,
                parentPost = req.parentPost,
                parentComment = req.parentComment,
                userID = req.userID
            )

        except Exception as e:
            print(f"[ERROR]: {e}")
        
        finally:
            self.conn.close()
            return ret


    def readComments(self, request, context):
        self.makeConnection()
        allComments = self.collection.find({})


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    comments_pb2_grpc.add_commentServiceServicer_to_server(
        commentServiceServicer(),server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    logging.basicConfig()
    serve()