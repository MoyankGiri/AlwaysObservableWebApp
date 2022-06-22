import logging
from datetime import date, datetime, timedelta

from concurrent import futures
from multiprocessing.sharedctypes import Value
import re
from time import strftime, strptime

import grpc
import prometheus_client
from app.helpers.error_middlewear import count_error
from py_grpc_prometheus.prometheus_server_interceptor import PromServerInterceptor

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
            res = self.collection.delete_one({"_id":ObjectId(req.id),"userID":req.userID})
            if not res.acknowledged:
                raise ValueError("Unable to delete record from db!")
        except Exception as e:
            print(e)
            count_error('GET','deletePost','post not present in database')
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
            count_error('POST','updateBlog','blog not found')
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

    #return posts of a specific user
    def authorPosts(self,req,ctx):
        self.makeConnection()
        
        try:
            posts = self.collection.find({'userID':req.userID})
            print("Posts found are: ",posts)
            all_posts = post_pb2.Posts()
            for row in posts:
                all_posts.posts.append(post_pb2.postPreview(title=row['title'],author=row['author'],creationDate=str(row['creationDate']),id=str(row['_id'])))
            self.conn.close()
            return all_posts
        except Exception as e:
            print("[Error]:",e)
            self.conn.close()
            return post_pb2.Posts()
            
    def create(self,req,ctx):
        self.makeConnection()
        print("Creating entry....")
        ret = None
        print(req.title)
        print(req.body)
        print(req.userID)
        # today = date.today().strftime("%d-%m-%y")
        today = datetime.now()
        try:
            #check if any field is empty
            if not req.title or not req.body or not today or not req.userID:
                print("Data not provided for post creation!")
                count_error('POST','createBlog','no data to exreate blog')
                raise ValueError("No data to create post!")

            print("Blog created by:",req.userID)

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
            self.conn.close()
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
            self.conn.close()
            return ret

    def fetchRecent(self,req,ctx):
        self.makeConnection()

        allPosts = post_pb2.Posts()
        # constraint = datetime.now() - timedelta(minutes=int(req.duration))
        constraint = datetime.now() - timedelta(minutes=int(1000))

        allRows = self.collection.find({})
        print("Posts found are: ",allRows)

        num_posts=0
        for row in allRows:
            print(f'ROW {row}')
            currDate = row['creationDate']
            if currDate > constraint:
                allPosts.posts.append(post_pb2.postPreview(title=row['title'],author=row['author'],creationDate=str(row['creationDate']),id=str(row['_id'])))
                num_posts+=1

        if num_posts==0:
            count_error("GET","fetchPosts","no posts to fetch!")  
            print("No posts found :(")

        return allPosts

    def readOne(self,req,ctx):
        print("req:",req)
        self.makeConnection()
        ret = None

        try:
            row = self.collection.find_one({"_id":ObjectId(req.id)})
            print("row obtained",row)

            if not row:
                raise ValueError("No object found in db!")
            else:
                self.conn.close()

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
            self.conn.close()

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

    #grpc interceptor
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10),interceptors=(PromServerInterceptor()))

    post_grpc.add_postServiceServicer_to_server(
        postServiceServicer(),server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == "__main__":
    logging.basicConfig()
    prometheus_client.start_http_server(6996)
    serve()

