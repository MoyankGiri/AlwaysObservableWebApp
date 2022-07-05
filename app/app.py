from datetime import datetime
import json
import os
from random import randint
from flask import Response, flash, jsonify, make_response, render_template_string, request
import grpc
from prometheus_client import start_http_server
from py_grpc_prometheus.prometheus_client_interceptor import PromClientInterceptor
import time


DOCKER = True
debugFlag = 1

import sys

if DOCKER:
    sys.path.insert(1,'/webapp/microservices/post_svc/src')
    sys.path.insert(1,'/webapp/microservices/auth_svc/src')
    sys.path.insert(1,'/webapp/microservices/comments_svc/src')
    sys.path.insert(1,'/webapp/helpers')
else:
    sys.path.insert(0,'/home/chandradhar/Projects/CTY/AlwaysObservableWebApp/microservices/auth_svc/src')
    sys.path.insert(0,'/home/chandradhar/Projects/CTY/AlwaysObservableWebApp/microservices/post_svc/src')
    sys.path.insert(0,'/home/chandradhar/Projects/CTY/AlwaysObservableWebApp/microservices/comments_svc/src')
    sys.path.insert(0,'/home/chandradhar/Projects/CTY/AlwaysObservableWebApp/helpers')
    # sys.path.insert(0,'C:/Users/moyan/Desktop/HPCTY/AlwaysObservableWebApp/microservices/auth_svc/src')
    # sys.path.insert(0,'C:/Users/moyan/Desktop/HPCTY/AlwaysObservableWebApp/microservices/post_svc/src')
    # sys.path.insert(0,'C:/Users/moyan/Desktop/HPCTY/AlwaysObservableWebApp/microservices/comments_svc/src')
    # sys.path.insert(0,'C:/Users/moyan/Desktop/HPCTY/AlwaysObservableWebApp/helpers')

import user_pb2_grpc,user_pb2
import post_pb2_grpc,post_pb2
import comments_pb2
import comments_pb2_grpc

#---------docker related stuff--------

#(will need to change mongoDB connection to DB as shown below for posts and auth)
# client = pymongo.MongoClient(os.environ.get('DB'))
commentMicroServiceOSENV = os.environ.get('CommentMicroService')
postMicroServiceOSENV = os.environ.get('PostMicroService')
authMicroServiceOSENV = os.environ.get('AuthMicroService')

#---------docker related stuff end--------
from flask import Flask,render_template,request
app = Flask(__name__)
app.secret_key = 'abc'


#Prometheus client will send the metrics to the server
#****************Prometheus*****************************
from py_grpc_prometheus.prometheus_client_interceptor import PromClientInterceptor as grpc_interceptor
posts_client_metrics = 8000
users_client_metrics = 8069

import prometheus_client

from middlewear import setup_metrics
from error_middlewear import count_error
from other_middlewears import measure_blog_latency
from other_middlewears import increment_blog_comments
from other_middlewears import inc_blog_edits

setup_metrics(app)
#****************Prometheus Ends*****************************

#*********GRPC Client Code*******************************
class apiClient:
    def __init__(self) -> None:
        #good practice to reuse channels and stubs across multiple connections

        if DOCKER:
            #create an interceptor for posts client-stub
            post_channel = grpc.intercept_channel(
                grpc.insecure_channel("postmicroservice:50051"),
                grpc_interceptor()
            )
            prometheus_client.start_http_server(8011)

            user_channel = grpc.insecure_channel("authmicroservice:50056")
            print(f"Post Channel {post_channel}")
            print(f"User Channel {user_channel}")
        else:
            #create an interceptor for posts client-stub
            post_channel = grpc.intercept_channel(
                grpc.insecure_channel('localhost:50051'),
                grpc_interceptor()
            )
            prometheus_client.start_http_server(8011)

            user_channel = grpc.insecure_channel("localhost:50056")
            print(f"Post Channel {post_channel}")
            print(f"User Channel {user_channel}")

        self.user_stub = user_pb2_grpc.userServiceStub(user_channel)
        self.post_stub = post_pb2_grpc.postServiceStub(post_channel)
    
    def signup(self,username,password):
        print(f"********{username},{password}********")

        response = self.user_stub.createAccount(user_pb2.aUser(username=username,password=password))
        print("Recieved from GRPC:",response)

        if response!=None:
            return response
        else:
            print("Couldnt recieve response from grpc server")

    def createBlog(self,title,body,author,userID):
        post = {
                'id ': "",
                'title' : "",
                'body' : "",
               'author' : "",
                'creationDate' : "",
                'lastUpdatedDate' : "",
                'userID':""
                }
        try:
            post = self.post_stub.create(post_pb2.newPost(title=title,body=body,author=author,userID=userID))
            print("User's post:",post)
            return post

        except Exception as e:
            print("[ERROR]:",e)
            return post

    def signup(self,username,password):
        print(f"********{username},{password}********")
        success = {'success':False}
        try:
            success = self.user_stub.createAccount(user_pb2.aUser(username=username,password=password))
            print(success)
        except Exception as e:
            print(f"[ERROR]: {e}")
            print(f"Success {success}")
            return success
            
            
    def delete_post(self,blogid,userid):
        print(f"********{blogid,userid}********")
        isSuccess={'success':False}
        try:
            isSuccess = self.post_stub.deletePost(post_pb2.uid(id=blogid,userID=userid))
            return isSuccess
        except Exception as e:
            print(f"Error {e}")
            return isSuccess

    def signin(self,username,password):
        print(f"********{username},{password}********")
        session = {'success':0,'msg':'','token':'','timelimit':''}
        try:
            session = self.user_stub.login(user_pb2.aUser(username=username,password=password))
            print(session)
            return session
        except Exception as e:
            print(f'[ERROR]: {e}')
            return session
        finally:
            print(f"success {session}")
            return session

    def authorize_user(self,token):
        print("Auth Middlewear kickin...")
        result = None
        try:
            print(f"try with token {token}")
            result = self.user_stub.auth(user_pb2.header(token=str(token)))
            print(f"result {result}")
            print(result.success == True)

            if not result or not result.success:
                raise Exception("User not authenticated")
            else:
                print("Succssful auth!")
                return result
        except Exception as e:
            print("Unsuccessful auth :(")
            count_error('POST','authToken','unable to authorize user')
            print(e)
            print(e)
            return result

    def read_all(self,t):
        result = []

        try:
            result = self.post_stub.fetchRecent(post_pb2.when(duration=100000))
            # print("All posts are:",result)
            return result.posts

        except Exception as e:
            print("[ERROR]",e)

        return result

    def read_one(self,blogid):
        post = None
        try:
            post = self.post_stub.readOne(post_pb2.uid(id=blogid))
            return post
        except Exception as e:
            print("[ERROR]:",e)

    def read_home(self,userID):
        all_posts = None
        try:
            all_posts = self.post_stub.authorPosts(post_pb2.userIdentification(userID=userID))
            return all_posts.posts
        except Exception as e:
            print("[ERROR]",e)
        return all_posts

    def edit_blog(self,blogid,userid,postDict):
        print(f"Editing blog:{blogid}\nCreated by:{userid}")
        updatedPost = {}
        try:
            updatedPost = self.post_stub.updatePost((post_pb2.aPost(
                id=postDict['blogid'],
                title=postDict['title'],
                body=postDict['body'],
                author=postDict['author'],
                creationDate=str(datetime.now()),
                lastUpdatedDate=str(datetime.now()),
                userID=userid
            )))
            print("Updated Post!!!!")
            return updatedPost
        except Exception as e:
            print(f"[Error]",e)
            return updatedPost

class appClient:

    def __init__(self) -> None:
        if DOCKER:
            print(commentMicroServiceOSENV,file=sys.stderr)
            #commentChannel = grpc.intercept_channel(grpc.insecure_channel(f"{commentMicroServiceOSENV}:5051"),PromClientInterceptor())
            commentChannel = grpc.insecure_channel(f"{commentMicroServiceOSENV}:5051")
            if debugFlag: print(f"app.py: Comment Channel {commentChannel}",file=sys.stderr)
            self.comment_stub = comments_pb2_grpc.commentServiceStub(commentChannel)
            #start_http_server(5052) # client metrics is located at http://localhost:5052
            if debugFlag: print(f"app.py: comment stub: {self.comment_stub}",file=sys.stderr)
        else:
            commentChannel = grpc.insecure_channel("localhost:5051")
            self.comment_stub = comments_pb2_grpc.commentServiceStub(commentChannel)
    
    def create_comment(self,title,body,author,parentpost,userid):
        newComment = None
        try:

            newComment = self.comment_stub.createComment(comments_pb2.aComment(title = title,body = body,author = author,parentPost = parentpost,parentComment = "root",userID = userid))
            if debugFlag: print(f"app.py: new Comment object: {newComment}",file=sys.stderr)
        except Exception as e:
            print(f"[ERROR]: {e}")
        finally:
            if not (newComment.title and newComment.body and newComment.author):
                print("ERROR")
                return 
            try:
                commentResponseReceived = self.comment_stub.GetCreatedComment(comments_pb2.CreatedCommentResponse(commentID = str(newComment.id)))
                if debugFlag: print(f"app.py: Comment Response Received in create_comment: {commentResponseReceived}")
                return commentResponseReceived
            except Exception as e:
                print(f"[ERROR]: {e}")
    
    def readComments(self,BlogID):
        res = []
        try:
            res = self.comment_stub.readComments(comments_pb2.blogID(blogid = BlogID))
            print(f"app.py: fetched Comments: {res}",file=sys.stderr)
            return res.comments
        except Exception as e:
            print(f"[ERROR]: {e}",file=sys.stderr)
        return res

    def GetCreatedComment(self, request, context):
        self.makeConnection()
        createdComment = (self.collection.find({"_id":ObjectId(request.commentID)}))[0]
        if debugFlag: print(f"app.py: createdComment Object {createdComment}")
        return comments_pb2.commentItem(id = request.commentID,title = createdComment["title"],body = createdComment["body"],author = createdComment["author"],parentPost = createdComment["parentPost"],parentComment = createdComment["parentComment"],userID = createdComment["userID"])



#*********GRPC Client Code ENDS*******************************

apic = apiClient()

#**put this to the apiClient class itself please**
appclient = appClient()

@app.route("/metrics")
def metrics():
    #create and send response to the prometheus querying server
    return Response(prometheus_client.generate_latest(),mimetype=str('text/plain; version=0.0.4; charset=utf-8'))

@app.route("/",methods=['GET'])
def landing():
    return render_template('login.html')

@app.route("/logout",methods=['GET'])
def logout():
    resp = make_response(render_template('success.html'))
    resp.delete_cookie('token')
    return resp

@app.route("/createAccount",methods=['POST','GET'])
def createAccount():
    if request.method=='POST':
        response = apic.signup(request.form.get('username'),request.form.get('password'))
        print(f"Recieved from API client object server : {response}")

        if response!=None and response.success:
            #render success page and redirect to login UI
            # flash(response.msg)
            return render_template('login.html')
        elif response!=None:
            #render the create Account page again
            # flash(response.msg)
            return render_template('signup.html')
        else:
            return render_template('login.html')

    elif request.method=='GET':
        return render_template('signup.html')

@app.route("/login",methods=['POST','GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method=='POST':
        try:
            session = apic.signin(request.form.get('username'),request.form.get('password'))
            print(f"Login session *****{session}*****")

            if session.success:
                # flash(session.msg)
                response = make_response(render_template('homepage.html'))
                response.set_cookie('token',session.token)
                return response
            else:
                response = make_response(render_template('login.html'))
                return response

        except Exception as e:
            return render_template('login.html')

@app.route("/createBlog",methods=['POST','GET'])
def createBlog():
    print(f"******{request.form}****")
    # authRes = await authroize_user(request.headers['Token'])
    authRes = apic.authorize_user(request.cookies.get('token'))
    print(authRes)
    try:
        if authRes.success:
            print("Authorized user!!!")
        if request.method == 'GET':
            print("Redirect to create blog....")
            return render_template('create_blog.html')
        elif request.method == 'POST':
            aPost = apic.createBlog(request.form.get('title'),request.form.get('body'),request.form.get('author'),authRes.userID)
            if aPost.id!='':
                return render_template('success.html')
            else:
                return render_template('failed.html')
    except Exception as e:
        print(e)
        count_error('POST','createBlog','Unauthorized access')
        return render_template('login.html')
       

@app.route("/readBlogs",methods=['GET'])
def readBlogs():
    #read all blocks,no need to login
    result = apic.read_all(7)
    if request.method=='GET':
        if result:
            # print("Result",list(result))
            #display in the UI
            return render_template("display_blog.html",items=list(result))
        else:
            #display empty page
            print("Nothing to fetch :(")
            return render_template("failed.html")
    else:
        return render_template("homepage.html")

@app.route("/fetchBlogs",methods=['GET'])
def fetchBlogs():
    #read all blocks,no need to login
    result = apic.read_all(7)
    blogs = []
    for post in list(result):
        blogs.append((post.id))
    if request.method=='GET':
        if result:
            result = {'data':blogs}
            return Response(json.dumps(result),mimetype='application/json')
        else:
            return []

@app.route("/home",methods=['GET'])
def homepage():
    #find out the logged in user
    authRes = apic.authorize_user(request.cookies.get("token"))
    print("authRes",authRes)

    if authRes.success:
        print("User authorized!")
        if request.method=='GET':
            all_posts = apic.read_home(authRes.userID)
            print("Posts retrieved:",all_posts)
            return render_template("homepage.html",items=list(all_posts)[::-1])
    else:
        count_error('GET','home','Unauthorized access')
        return render_template("failed.html")

@app.route("/editBlog",methods=['GET','POST'])
def updateBlog():
    authRes = apic.authorize_user(request.cookies.get("token"))

    if authRes.success:
        if request.method=='POST':
            try:
                print("User Authorized,Updating the blog content....")
                print()

                print("Recieved blogid",request.form.to_dict())
                res_data = request.form.to_dict()
                updatedBlog = apic.edit_blog(res_data["blogid"],authRes.userID,request.form.to_dict())
                print("Blog article updated!",updatedBlog)
                return render_template("success.html")
            except Exception as e:
                return render_template("failed.html")
        else:
            if request.method=='GET':
                inc_blog_edits(request.args.get("blogid"))

                #return the blog with the earlier data
                aBlog = apic.read_one(request.args.get("blogid"))
                print("Ablog:",aBlog)
                return render_template('edit_blog.html',article=aBlog)

@app.route("/deleteBlog",methods=['GET'])
def deleteBlog():
    try:
        #check if the blog actually belongs to him
        authRes = apic.authorize_user(request.cookies.get("token"))
        if authRes.success:
            print("User Authorized!!")
            if request.method == 'GET':
                isSuccess = apic.delete_post(request.args.get("blogid"),authRes.userID)
                print("isSuccess",isSuccess)
                if isSuccess.success:
                    return render_template('success.html')
                else:
                    count_error('GET','deleteBlog','Unauthorized access')
                    return render_template('failed.html')
        else:
            return render_template('failed.html')

    except Exception as e:
        print(e)
        return render_template('failed.html')

@app.route("/readOne",methods=['GET'])
def readOne():
    if request.method=='GET':
        #start timer to measure blogRead latency
        start = time.time()

        aPost = apic.read_one(request.args.get('blogid'))
        res = appclient.readComments(request.args.get('blogid'))
        print("Retrieved a single blog: ",aPost)

        #end time when blog is read
        time.sleep(randint(1,3))
        end = time.time()
        #update the time taken
        measure_blog_latency(end-start,request.args.get('blogid'),aPost.title)
        print(f"The blog {request.args.get('blogid')} took: ",end-start,"to load!")

        if aPost:
            return render_template('aPost.html',post=aPost,items=list(res))
        else:
            return render_template('failed.html')

@app.route("/createComment",methods = ['GET','POST'])
def createComment():
    authRes = apic.authorize_user(request.cookies.get('token'))
    print(authRes)
    try:
        if authRes.success:
            print("Authorized user!!!")
        if request.method == 'POST':
            title = request.form['title']
            author = request.form['author']
            body = request.form['body']
            blogid = request.form['blogID']
            try:
                print("Calling here server",file=sys.stderr)
                commentResponseReceived = appclient.create_comment(title,body,author,blogid,authRes.userID)
                print(commentResponseReceived,file=sys.stderr)

                #counter for comments on a particular blog
                increment_blog_comments(blogid)

            except Exception as e:
                print(f"[ERROR]: {e}")
            finally:
                if not commentResponseReceived.id:
                    return render_template('failed.html')
                else:
                    return render_template('success.html')
        else:
            aPost = apic.read_one(request.args.get('blogid'))
            return render_template('commentInput.html',post=aPost,blogid = request.args.get('blogid'))
    except Exception as e:
        print(e)
        render_template('login.html')

        

if __name__ == '__main__':
    app.debug = False
    app.run(host = '0.0.0.0',port=5000)