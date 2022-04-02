from flask import Flask, jsonify, redirect,render_template, render_template_string,request, url_for
import pymongo
import sys

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["blog"]
MongoPostsCollection = db["postsDB"]

app = Flask(__name__)

@app.route("/")
def helloWorld():
    return render_template("Home.html")

@app.route("/addData",methods = ['GET','POST'])
def insertIntoDatabase():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        data = {'title' : title,'content' : content}
        MongoPostsCollection.insert_one(data)
        return redirect(url_for("helloWorld"))
    return render_template('inputData.html')

@app.route("/getData")
def getFromDatabase():
    try:
        AllDocs = MongoPostsCollection.find({})
        st = ""
        for i in AllDocs:
            print(i, file=sys.stderr)
            st += "<h2>" + str(i['title']) + "</h2> <p>" + str(i['content']) + "</p> <br>"
        return render_template_string('<!DOCTYPE html> <html lang="en"><head><meta charset="UTF-8"><meta http-equiv="X-UA-Compatible" content="IE=edge"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head><body>' + st + '</body></html>')
    except Exception as e:
        print(e, file=sys.stderr)
        return jsonify(success = False)


if __name__ == '__main__':
    app.run(host = '127.0.0.1',debug=True)