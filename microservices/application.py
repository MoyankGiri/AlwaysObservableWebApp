from distutils.log import debug
from urllib import response
from flask import Flask,Response

def create_app():
    app = Flask(__name__)

    @app.route("/",methods=['GET'])
    def dummy():
        return Response("Blog App!")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host = '127.0.0.1',port=5000,debug=True)
    