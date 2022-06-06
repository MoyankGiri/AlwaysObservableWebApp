import os
from flask import Response, flash, jsonify, make_response, render_template_string, request
import grpc
from prometheus_client import start_http_server
from py_grpc_prometheus.prometheus_client_interceptor import PromClientInterceptor

DOCKER = True
debugFlag = 1

import sys
if DOCKER:
    sys.path.insert(1,'/webapp/microservices/post_svc/src')
    sys.path.insert(1,'/webapp/microservices/auth_svc/src')
    sys.path.insert(1,'/webapp/microservices/comments_svc/src')
else:
    sys.path.insert(0,'/home/chandradhar/Projects/CTY/AlwaysObservableWebApp/microservices/auth_svc/src')
    sys.path.insert(0,'/home/chandradhar/Projects/CTY/AlwaysObservableWebApp/microservices/post_svc/src')
    sys.path.insert(0,'/home/chandradhar/Projects/CTY/AlwaysObservableWebApp/microservices/comments_svc/src')

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

#*********GRPC Client Code*******************************
class apiClient:
    def __init__(self) -> None:
        #good practice to reuse channels and stubs across multiple connections
        post_channel = grpc.insecure_channel("postmicroservice:50051")
        user_channel = grpc.insecure_channel("authmicroservice:50056")
        print(f"Post Channel {post_channel}")
        print(f"User Channel {user_channel}")
        self.user_stub = user_pb2_grpc.userServiceStub(user_channel)
        self.post_stub = post_pb2_grpc.postServiceStub(post_channel)
    
    def signup(self,username,password):
        print(f"********{username},{password}********")
        success = {'success': False}
        try:
            success = self.user_stub.createAccount(user_pb2.aUser(username=username,password=password))
            print(success)
        except Exception as e:
            print(f"[ERROR]: {e}")
        finally:
            print(f"Success {success}")
            return success

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
        try:
            success = self.user_stub.createAccount(user_pb2.aUser(username=username,password=password))
            print(success)
        except Exception as e:
            print(f"[ERROR]: {e}")
        finally:
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
            print(e)
            return result

    def read_all(self,t):
        result = []

        try:
            result = self.post_stub.fetchRecent(post_pb2.when(duration=t*24*60))
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
                id=postDict['id'],
                title=postDict['title'],
                body=postDict['body'],
                author=postDict['author'],
                creationDate=postDict['creationDate'],
                lastUpdatedDate=postDict['lastUpdatedDate'],
                userID=userid
            )))
            return updatedPost
        except Exception as e:
            print(f"[Error]",e)
            return updatedPost

class appClient:

    def __init__(self) -> None:
        print(commentMicroServiceOSENV,file=sys.stderr)
        #commentChannel = grpc.intercept_channel(grpc.insecure_channel(f"{commentMicroServiceOSENV}:5051"),PromClientInterceptor())
        commentChannel = grpc.intercept_channel(grpc.insecure_channel(f"{commentMicroServiceOSENV}:5051"),PromClientInterceptor())
        if debugFlag: print(f"app.py: Comment Channel {commentChannel}",file=sys.stderr)
        self.comment_stub = comments_pb2_grpc.commentServiceStub(commentChannel)
        #start_http_server(5052) # client metrics is located at http://localhost:5052
        if debugFlag: print(f"app.py: comment stub: {self.comment_stub}",file=sys.stderr)
    
    def create_comment(self,title,body,author):
        newComment = None
        try:

            newComment = self.comment_stub.createComment(comments_pb2.aComment(title = title,body = body,author = author,parentPost = "root",parentComment = "root",userID = "1"))
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
    def GetCreatedComment(self, request, context):
        self.makeConnection()
        createdComment = (self.collection.find({"_id":ObjectId(request.commentID)}))[0]
        if debugFlag: print(f"app.py: createdComment Object {createdComment}")
        return comments_pb2.commentItem(id = request.commentID,title = createdComment["title"],body = createdComment["body"],author = createdComment["author"],parentPost = createdComment["parentPost"],parentComment = createdComment["parentComment"],userID = createdComment["userID"])



#*********GRPC Client Code ENDS*******************************

apic = apiClient()

#**put this to the apiClient class itself please**
appclient = appClient()

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
        success = apic.signup(request.form.get('username'),request.form.get('password'))
        if success.success:
            #render success page and redirect to login UI
            flash(success.msg)
            return render_template('login.html')
        else:
            #render the create Account page again
            flash(success.msg)
            return render_template('signup.html')
    elif request.method=='GET':
        return render_template('signup.html')

@app.route("/login",methods=['POST','GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method=='POST':
        session = apic.signin(request.form.get('username'),request.form.get('password'))
        print(f"Login session *****{session}*****")

        try:
            if session.success:
                # flash(session.msg)
                response = make_response(render_template('homepage.html'))
                response.set_cookie('token',session.token)
                return response
            else:
                # flash(session.msg)
                response = make_response(render_template('login.html'))
                return response
        except Exception as e:
            print(f'Error {e}')
            return render_template('login.html')

@app.route("/createBlog",methods=['POST','GET'])
def createBlog():
    print(f"******{request.form}****")
    # authRes = await authroize_user(request.headers['Token'])
    authRes = apic.authorize_user(request.cookies.get('token'))
    print(authRes)
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
    else:
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
        return render_template("failed.html")

@app.route("/editBlog",methods=['GET','POST'])
def updateBlog():
    authRes = apic.authorize_user(request.cookies.get("token"))
    if authRes.success:
        if request.method=='POST':
            print("User Authorized,Updating the blog content....")
            updatedBlog = apic.edit_blog(request.args.get("blogid"),authRes.userID,request.form.to_dict())
            print("Blog article updated!",updatedBlog)
            return render_template("success.html")
        else:
            if request.method=='GET':
                #return the blog with the earlier data
                aBlog = apic.read_one(request.args.get("blogid"))
                return render_template('edit_blog.html',article=aBlog)

@app.route("/deleteBlog",methods=['GET'])
def deleteBlog():
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
                return render_template('failed.html')
    else:
        return render_template('failed.html')

@app.route("/readOne",methods=['GET'])
def readOne():
    if request.method=='GET':
        aPost = apic.read_one(request.args.get('blogid'))
        print("Retrieved a single blog: ",aPost)
        if aPost:
            return render_template('aPost.html',post=aPost)
        else:
            return render_template('failed.html')

@app.route("/createComment",methods = ['GET','POST'])
def commentCreate():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        body = request.form['body']
        try:
            print("Calling here server",file=sys.stderr)
            commentResponseReceived = appclient.create_comment(title,body,author)
            print(commentResponseReceived,file=sys.stderr)
        except Exception as e:
            print(f"[ERROR]: {e}")
        finally:
            if not commentResponseReceived.id:
                print("ERROR")
                return 
            st = "<h2>" + str(commentResponseReceived.title) + "</h2> <h3>" + str(commentResponseReceived.author) +  "</h3> <p>" + str(commentResponseReceived.id) + "<br>" + str(commentResponseReceived.userID) + "<br>" + str(commentResponseReceived.body) + "<br>"
            try:
                return render_template_string('<!DOCTYPE html> <html lang="en"><head><meta charset="UTF-8"><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head><body>' + st + '</body></html>')
            except Exception as e:
                print(f"[ERROR]: {e}")
                return jsonify(success = False)
    else:
        return render_template('commentInput.html')
        

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0',port=5000)