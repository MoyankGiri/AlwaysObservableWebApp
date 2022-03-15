import logging
from datetime import date

from concurrent import futures
import grpc

import post_pb2
import post_pb2_grpc as post_grpc

class postServiceServicer(post_grpc.postServiceServicer):
    def __init__(self):
        self.len = 0
        db = open("db.txt",'r')
        for _ in db.readlines():
            self.len+=1

    def create(self,req,ctx):
        db = self.db = open("db.txt","a")
        today = date.today().strftime("%d/%m/%y")
        line = [f'{self.len}',req.title,req.body,req.author,today,today]
        db.write("\n"+",".join(line))
        self.len+=1
        db.close()
        return post_pb2.aPost(
            id=f"{self.len}",
            title=req.title,
            body=req.body,
            author=req.author,
            creationDate=today,
            lastUpdatedDate=today
        )

    def readOne(self,req,ctx):
        print("req:",req)
        line = None
        db = open("db.txt","r")
        lines = db.readlines()
        for l in lines:
            l = l.split(",")
            if l[0]==req.id:
                line = l
                print("Match found!")
                break

        db.close()
        if not line:
            return post_pb2.aPost(
                id = "",
                title = "",
                body = "",
                author = "",
                creationDate = "",
                lastUpdatedDate = "",
                )
        else:
            return post_pb2.aPost(
                id=line[0],
                title=line[1],
                body=line[2],
                author=line[3],
                creationDate=line[4],
                lastUpdatedDate=line[5]
                )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    post_grpc.add_postServiceServicer_to_server(
        postServiceServicer(),server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    logging.basicConfig()
    serve()

