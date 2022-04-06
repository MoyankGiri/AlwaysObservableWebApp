import asyncio
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
async def signup(username,password):
    print(f"********{username},{password}********")
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        success = {'success': False}
        try:
            stub = user_pb2_grpc.userServiceStub(channel)
            success = await stub.createAccount(user_pb2.aUser(username=username,password=password))
            print(success)
        except Exception as e:
            print(f"[ERROR]: {e}")
        finally:
            print(f"Success {success}")
            return success

async def signin(username,password):
    print(f"********{username},{password}********")
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        success = {'success':0,'msg':'','token':'','timelimit':''}
        try:
            stub = user_pb2_grpc.userServiceStub(channel)
            success = await stub.login(user_pb2.aUser(username=username,password=password))
            print(success)
            return success
        except Exception as e:
            print(f'[ERROR]: {e}')
        finally:
            print(f"success {success}")

async def authroize_user(token):
    print("Auth Middlewear kickin...")
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        result = None
        try:
            print(f"try with token {token}")
            stub = user_pb2_grpc.userServiceStub(channel)
            result = await stub.auth(user_pb2.header(token=str(token)))
            print(f"Success {result}")
            print(result.success == True)

            if not result or not result.success:
                raise Exception("User not authenticated")
            else:
                print("Succssful auth!")
                return True
        except Exception as e:
            print("Unsuccessful auth :(")
            print(e)
            return False

async def makeBlog(blog):
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        try:
            aPost = None
            stub = post_pb2_grpc.postServiceStub(channel)
            aPost = await stub.create(post_pb2.newPost(title=blog['title'],body=blog['body'],author=blog['author']))

            if not aPost or aPost.id=='':
                raise Exception("Empty posts")
            else:
                return render_template('display_blog.html',result=aPost)
        except Exception as E:
            flash("Unable to create Post,try again...")
            return render_template('create_blog.html')

#*********GRPC Client Code*******************************

#**********ROUTES**************************************

@app.route("/",methods=['GET'])
def homePage():
    return render_template('login.html')

@app.route("/createAccount",methods=['POST','GET'])
async def createAccount():
    if request.method=='POST':
        success = await signup(request.form.get('username'),request.form.get('password'))
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
async def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method=='POST':
        session = await  signin(request.form.get('username'),request.form.get('password'))
        if session.success:
            flash(session.msg)
            response = make_response(render_template('homepage.html'))
            response.set_cookie('token',session.token)
            return response
        else:
            flash(session.msg)
            response = make_response(render_template('login.html'))
            return response

@app.route("/createBlog",methods=['POST','GET'])
async def createBlog():
    # authRes = await authroize_user(request.headers['Token'])
    authRes = await authroize_user(request.cookies.get('token'))
    if authRes:
        print("Authorized user!!!")
        if request.method == 'GET':
            print("Redirect to create blog....")
            return render_template('create_blog.html')
        elif request.method == 'POST':
            return render_template('create_blog.html')
    else:
        return render_template('login.html')

#**********ROUTES**************************************

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0',port=5000)