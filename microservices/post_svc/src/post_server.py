import logging
from datetime import date, datetime, timedelta
import os
from concurrent import futures
from multiprocessing.sharedctypes import Value
from time import strftime, strptime
import grpc

import post_pb2
import post_pb2_grpc as post_grpc

import pymongo
from pymongo.collection import ReturnDocument
from bson.objectid import ObjectId

class postServiceServicer(post_grpc.postServiceServicer):
    def __init__(self) -> None:
        super().__init__()

        print("Creating connection to mongodb....")
        print("To connect to",os.environ.get("DB") or "mongodb://localhost:27017/")
        self.conn = pymongo.MongoClient(os.environ.get('DB') or "mongodb://localhost:27017/")
        self.db = self.conn["blog_app"]
        self.collection = self.db["posts"]
        print("Made connections to post db!")

        # print("Deleting data...")
        # self.collection.delete_many({})

    def deletePost(self,req,ctx):
        print("Deleting record....")
        res = False

        try:
            print("req",req)
            res = self.collection.delete_one({"_id":ObjectId(req.id),"userID":req.userID})
            if not res.acknowledged:
                raise ValueError("Unable to delete record from db!")
        finally:
            return post_pb2.isSuccess(success=res.acknowledged)

    def updatePost(self,req,ctx):
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
            
            return ret

    #return posts of a specific user
    def authorPosts(self,req,ctx):
        try:
            posts = self.collection.find({'userID':req.userID})
            print("Posts found are: ",posts)
            all_posts = post_pb2.Posts()
            for row in posts:
                all_posts.posts.append(post_pb2.postPreview(title=row['title'],author=row['author'],creationDate=str(row['creationDate']),id=str(row['_id'])))
            
            return all_posts
        except Exception as e:
            print("[Error]:",e)
            
            return post_pb2.Posts()
            
    def create(self,req,ctx):
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
                "lastUpdatedDate":today,
                "userID":req.userID
            }
            print("Data to be inserted:",data)

            rec_id = self.collection.insert_one(data).inserted_id
            print("Commited post with id: ",rec_id)

            ret = post_pb2.aPost(
                id=f"{rec_id}",
                title=req.title,
                body=req.body,
                author=req.author,
                creationDate=today.strftime("%m/%d/%Y, %H:%M:%S"),
                lastUpdatedDate=today.strftime("%m/%d/%Y, %H:%M:%S"),
                userID=req.userID
            )
            print("returning:",ret)
            
            return ret
        except Exception as e:
            print("Exception?",e)
            ret = post_pb2.aPost(
                id = "",
                title = "",
                body = "",
                author = "",
                creationDate = "",
                lastUpdatedDate = "",
                userID=""
                )
            
            return ret

    def fetchRecent(self,req,ctx):
        allPosts = post_pb2.Posts()
        constraint = datetime.now() - timedelta(minutes=int(req.duration))

        allRows = self.collection.find({})
        for row in allRows:
            # print(f'ROW {row}')
            currDate = row['creationDate']
            if currDate > constraint:
                allPosts.posts.append(post_pb2.postPreview(title=row['title'],author=row['author'],creationDate=str(row['creationDate']),id=str(row['_id'])))
                
        return allPosts

    def readOne(self,req,ctx):
        print("req:",req)
        ret = None

        try:
            row = self.collection.find_one({"_id":ObjectId(req.id)})
            print("row obtained",row)

            if not row:
                raise ValueError("No object found in db!")
            else:
                return post_pb2.aPost(
                id=f'{req.id}',
                title=row["title"],
                body=row["body"],
                author=row["author"],
                creationDate=str(row["creationDate"]),
                lastUpdatedDate=str(row["lastUpdatedDate"]),
                userID=row["userID"]
                )
        except Exception as e:
            print("[ERROR]",e)
            return post_pb2.aPost(
                    id = "",
                    title = "",
                    body = "",
                    author = "",
                    creationDate = "",
                    lastUpdatedDate = "",
                    userID=""
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

