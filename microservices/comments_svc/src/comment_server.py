import logging
import os
from concurrent import futures
import grpc

import comments_pb2
import comments_pb2_grpc 

import pymongo
from pymongo.collection import ReturnDocument
from bson.objectid import ObjectId

class commentServiceServicer(comments_pb2_grpc.commentServiceServicer):

    def makeConnection(self):
        self.conn = pymongo.MongoClient(os.environ.get('DB'))
        #self.conn = pymongo.MongoClient("mongodb://localhost:27017/")
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
        Comments = self.collection.find({"userID":request.id})
        allComments = comments_pb2.CommentItemsList()
        for comment in Comments:
            allComments.comments.append(comments_pb2.aComment(title = comment["title"],body = comment["body"],author = comment["author"],parentPost = comment["parentPost"],parentComment = comment["parentComment"],userID = comment["userID"]))

        return allComments
    

    def GetCreatedComment(self, request, context):
        self.makeConnection()
        createdComment = (self.collection.find({"_id":ObjectId(request.commentID)}))[0]
        return comments_pb2.commentItem(id = request.commentID,title = createdComment["title"],body = createdComment["body"],author = createdComment["author"],parentPost = createdComment["parentPost"],parentComment = createdComment["parentComment"],userID = createdComment["userID"])



def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    comments_pb2_grpc.add_commentServiceServicer_to_server(
        commentServiceServicer(),server
    )
    print("Server is Running")
    server.add_insecure_port('[::]:5051')
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    logging.basicConfig()
    serve()

'''import logging
from datetime import date, datetime, timedelta
import os

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
        self.conn = pymongo.MongoClient(os.environ.get('DB'))
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
    '''
