import logging
from datetime import date, datetime, timedelta

from concurrent import futures
from time import strptime
import grpc

import post_pb2
import post_pb2_grpc as post_grpc

import pymongo
from pymongo.collection import ReturnDocument
from bson.objectid import ObjectId

class postServiceServicer(post_grpc.postServiceServicer):
    def makeConnection(self):
        # print("Creating connection to mongodb....")
        self.conn = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.conn["blog"]
        self.collection = self.db["posts"]

        # print("Deleting data...")
        # self.collection.delete_many({})

    def deletePost(self,req,ctx):
        self.makeConnection()
        print("Deleting record....")
        res = False

        try:
            print("req",req)
            res = self.collection.delete_one({"_id":ObjectId(req.id)})
            if not res.acknowledged:
                raise ValueError("Unable to delete record from db!")
        finally:
            return post_pb2.isSuccess(success=res.acknowledged)

    def updatePost(self,req,ctx):
        self.makeConnection()
        print("Updating record....")
        ret = None

        try:
            print("req",req)
            searchKey = ObjectId(req.id)

            row = self.collection.find_one_and_update({"_id":searchKey},{"$set":{
               "id" : req.id,
               "title":req.title,
               "body":req.body,
               "author":req.author,
               "creationDate":req.creationDate,
               "lastUpdatedDate":req.lastUpdatedDate
            }},return_document=ReturnDocument.AFTER)
            print("row",row)

            if row:
                print("Updated record!!")

                ret = post_pb2.aPost(
                id=f'{req.id}',
                title=row["title"],
                body=row["body"],
                author=row["author"],
                creationDate=row["creationDate"],
                lastUpdatedDate=row["lastUpdatedDate"]
                )
            else:
                raise ValueError("No doc updated!")
        except:
            ret = post_pb2.aPost(
                id = "",
                title = "",
                body = "",
                author = "",
                creationDate = "",
                lastUpdatedDate = "",
                )
        finally:
            self.conn.close()
            return ret
            
    def create(self,req,ctx):
        self.makeConnection()
        print("Creating row....")
        ret = None

        # today = date.today().strftime("%d-%m-%y")
        today = datetime.now()
        try:
            #insert row of data
            data = {
                "title":req.title,
                "body":req.body,
                "author":req.author,
                "creationDate":today,
                "lastUpdatedDate":today
            }
            rec_id = self.collection.insert_one(data)
            print("Commited....")

            ret = post_pb2.aPost(
                id=f"{rec_id.inserted_id}",
                title=req.title,
                body=req.body,
                author=req.author,
                creationDate=today,
                lastUpdatedDate=today
            )
        except:
             ret = post_pb2.aPost(
                id = "",
                title = "",
                body = "",
                author = "",
                creationDate = "",
                lastUpdatedDate = "",
                )
        finally:
            self.conn.close()
            return ret

    def fetchRecent(self,req,ctx):
        self.makeConnection()

        allPosts = post_pb2.Posts()
        constraint = datetime.now() - timedelta(minutes=int(req.duration))

        allRows = self.collection.find({})
        for row in allRows:
            # print(f'ROW {row}')
            currDate = row['creationDate']
            if currDate > constraint:
                allPosts.posts.append(post_pb2.postPreview(title=row['title'],author=row['author'],creationDate=str(row['creationDate'])))
                
        return allPosts

    def readOne(self,req,ctx):
        print("req:",req)
        self.makeConnection()
        ret = None

        try:
            row = self.collection.find_one({"_id":ObjectId(req.id)})
            print("row obtained",row)

            if not row:
                ret = post_pb2.aPost(
                    id = "",
                    title = "",
                    body = "",
                    author = "",
                    creationDate = "",
                    lastUpdatedDate = "",
                    )
            else:
                raise ValueError("No object found in db!")
        except:
            ret = post_pb2.aPost(
                id=f'{req.id}',
                title=row["title"],
                body=row["body"],
                author=row["author"],
                creationDate=row["creationDate"],
                lastUpdatedDate=row["lastUpdatedDate"]
                )
        finally:
            self.conn.close()
            return ret

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

