from doctest import Example
import logging
from datetime import date

from concurrent import futures
import re
import grpc

import post_pb2
import post_pb2_grpc as post_grpc

import sqlite3

class postServiceServicer(post_grpc.postServiceServicer):
    def makeConnection(self):
        self.conn = sqlite3.connect("post")
        self.cur = self.conn.cursor()

    def __init__(self):
        self.makeConnection()
        # self.cur.execute('''
        # drop table post;
        # ''')
        self.cur.execute('''
        create table if not exists post(id INTEGER primary key AUTOINCREMENT, title text not null,body text not null,author bigint not null,creationDate date not null,lastupdatedDate date not null);
        ''')
        self.conn.commit()
        self.conn.close()

    def create(self,req,ctx):
        print("Creating row....")
        self.makeConnection()

        today = date.today().strftime("%d-%m-%y")
        try:
            #insert row of data
            self.cur.execute(f'''
            insert into post (title,body,author,creationDate,lastUpdatedDate) values ('{req.title}','{req.body}','{req.author}','{today}','{today}');
            ''')
            self.conn.commit()
            self.conn.close()
            print("Commited....")

            return post_pb2.aPost(
                id=f"{self.cur.lastrowid}",
                title=req.title,
                body=req.body,
                author=req.author,
                creationDate=today,
                lastUpdatedDate=today
            )
        except:
             return post_pb2.aPost(
                id = "",
                title = "",
                body = "",
                author = "",
                creationDate = "",
                lastUpdatedDate = "",
                )


    def readOne(self,req,ctx):
        print("req:",req)
        self.makeConnection()

        # line = self.cur.execute('''
        # select * from post;
        # ''')
        # for r in line:
        #     print(r)

        line = self.cur.execute(f'''
            select * from post where id={int(req.id)};
        ''')

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
            for row in line:
                ret = post_pb2.aPost(
                    id=f'{row[0]}',
                    title=row[1],
                    body=row[2],
                    author=row[3],
                    creationDate=row[4],
                    lastUpdatedDate=row[5]
                    )
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

