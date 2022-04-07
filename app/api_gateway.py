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
            
    def delete_post(self,blogid):
        print(f"********{blogid}********")
        try:
            isSuccess = self.post_stub.deletePost(user_pb2.uuid(id=blogid))
            return isSuccess
        except Exception as e:
            print(f"Error {e}")
            return isSuccess

    def signin(self,username,password):
        print(f"********{username},{password}********")
        success = {'success':0,'msg':'','token':'','timelimit':''}
        try:
            success = self.user_stub.login(user_pb2.aUser(username=username,password=password))
            print(success)
            return success
        except Exception as e:
            print(f'[ERROR]: {e}')
            return success
        finally:
            print(f"success {success}")
            return success

    def authorize_user(self,token):
        print("Auth Middlewear kickin...")
        result = None
        try:
            print(f"try with token {token}")
            result = self.user_stub.auth(user_pb2.header(token=str(token)))
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

    def makeBlog(self,blog):
        try:
            aPost = None
            aPost = self.post_stub.create(post_pb2.newPost(title=blog['title'],body=blog['body'],author=blog['author']))

            if not aPost or aPost.id=='':
                raise Exception("Empty posts")
            else:
                return render_template('display_blog.html',result=aPost)
        except Exception as E:
            flash("Unable to create Post,try again...")
            return render_template('create_blog.html')

#*********GRPC Client Code*******************************

apic = apiClient()

@app.route("/",methods=['GET'])
def homePage():
    return render_template('login.html')

@app.route("/createAccount",methods=['POST','GET'])
async def createAccount():
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
async def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method=='POST':
        session = apic.signin(request.form.get('username'),request.form.get('password'))
        try:
            if session.success:
                flash(session.msg)
                response = make_response(render_template('homepage.html'))
                response.set_cookie('token',session.token)
                return response
            else:
                flash(session.msg)
                response = make_response(render_template('login.html'))
                return response
        except Exception as e:
            print(f'Error {e}')
            return render_template('login.html')

@app.route("/createBlog",methods=['POST','GET'])
async def createBlog():
    # authRes = await authroize_user(request.headers['Token'])
    authRes = apic.authorize_user(request.cookies.get('token'))
    if authRes:
        print("Authorized user!!!")
        if request.method == 'GET':
            print("Redirect to create blog....")
            return render_template('create_blog.html')
        elif request.method == 'POST':
            return render_template('create_blog.html')
    else:
        return render_template('login.html')

@app.route("/deleteBlog",methods=['POST','GET'])
async def deleteBlog():
    authRes = apic.authorize_user(request.cookies.get("token"))
    if authRes:
        print("User Authorized!!")
        if request.method == 'POST':
            isSuccess = apic.delete_post(request.form.get("blogid"))
            if isSuccess.success:
                return render_template('delete_success.html')
            else:
                return render_template('delete_fail.html')

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0',port=5000)