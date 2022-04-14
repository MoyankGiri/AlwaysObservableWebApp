from crypt import methods
from turtle import pos
from flask import flash, make_response, request
import grpc

import sys
sys.path.insert(0,'/home/chandradhar/Projects/CTY/AlwaysObservableWebApp/microservices/auth_svc/src')
sys.path.insert(0,'/home/chandradhar/Projects/CTY/AlwaysObservableWebApp/microservices/post_svc/src')
import user_pb2_grpc,user_pb2
import post_pb2_grpc,post_pb2

from flask import Flask,render_template,request
app = Flask(__name__)
app.secret_key = 'abc'

#*********GRPC Client Code*******************************
class apiClient:
    def __init__(self) -> None:
        #good practice to reuse channels and stubs across multiple connections
        post_channel = grpc.insecure_channel('localhost:50051')
        user_channel = grpc.insecure_channel('localhost:50056')
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
        result = {'success':False,'msg':'unsuccessful auth','userID':''}
        try:
            print(f"try with token {token}")
            result = self.user_stub.auth(user_pb2.header(token=str(token)))
            print(f"Success {result}")
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

#*********GRPC Client Code ENDS*******************************

apic = apiClient()

@app.route("/",methods=['GET'])
def landing():
    return render_template('login.html')

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
            aPost = apic.createBlog(request.form.get('title'),request.form.get('body'),request.form.get('body'),authRes.userID)
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
    if authRes.success:
        print("User authorized!")
        if request.method=='GET':
            all_posts = apic.read_home(authRes.userID)
            print("Posts retrieved:",all_posts)
            if all_posts:
                return render_template("homepage.html",items=list(all_posts))
            else:
                return render_template("failed.html")

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

@app.route("/readOne",methods=['GET'])
def readOne():
    if request.method=='GET':
        aPost = apic.read_one(request.args.get('blogid'))
        print("Retrieved a single blog: ",aPost)
        if aPost:
            return render_template('aPost.html',post=aPost)
        else:
            return render_template('failed.html')

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0',port=5000)