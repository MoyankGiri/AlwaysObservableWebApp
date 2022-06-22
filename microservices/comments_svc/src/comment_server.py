import logging
import os
from concurrent import futures
import grpc

import comments_pb2
import comments_pb2_grpc 

import pymongo
from pymongo.collection import ReturnDocument
from bson.objectid import ObjectId
from prometheus_client import start_http_server
from py_grpc_prometheus.prometheus_server_interceptor import PromServerInterceptor

class commentServiceServicer(comments_pb2_grpc.commentServiceServicer):

    def __init__(self) -> None:
        super().__init__()

        self.conn = pymongo.MongoClient(os.environ.get('DB'))
        #self.conn = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.conn["blog_app"]
        self.collection = self.db["comments"]
    

    def createComment(self,req,ctx):

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
            return ret


    def readComments(self, request, context):

        allComments = comments_pb2.CommentItemsList()
        print(f"comment_server.py: readComments (1): {request.blogid}")
        Comments = self.collection.find({"parentPost":request.blogid})
        for comment in Comments:
            allComments.comments.append(comments_pb2.aComment(title = comment["title"],body = comment["body"],author = comment["author"],parentPost = comment["parentPost"],parentComment = comment["parentComment"],userID = comment["userID"]))

        return allComments
    

    def GetCreatedComment(self, request, context):

        createdComment = (self.collection.find({"_id":ObjectId(request.commentID)}))[0]
        return comments_pb2.commentItem(id = request.commentID,title = createdComment["title"],body = createdComment["body"],author = createdComment["author"],parentPost = createdComment["parentPost"],parentComment = createdComment["parentComment"],userID = createdComment["userID"])



def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    #server = grpc.server(futures.ThreadPoolExecutor(max_workers=10),interceptors=(PromServerInterceptor(enable_handling_time_histogram=True, skip_exceptions=True),))
    comments_pb2_grpc.add_commentServiceServicer_to_server(
        commentServiceServicer(),server
    )
    print("Server is Running")
    server.add_insecure_port('[::]:5051')
    #start_http_server(5053) # server metrics is located at http://localhost:5053
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    logging.basicConfig()
    serve()