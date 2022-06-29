'''
Script to simulate workload:

->create blogs [done]
->create meaningful comments for various blogs [done]
->click meaningful blogs [done]
'''
import json
from random import *
import requests


MAX = 50

login_token = None
login_creds = {'username':'777','password':'7'}
blogs = []

def create_account(url):
    requests.post(url=url,data = login_creds)

def login(url):
    response = requests.post(url,login_creds)
    return {'token':response.cookies.get_dict()['token']}

def create_blog(url,token,title,author,content):
    requests.post(url,data={'title':title,'author':author,'body':content},cookies=token)


#login and create account
create_account('http://localhost:5000/createAccount')
login_token = login('http://localhost:5000/login')

#spam login and create account server to generate errors
count = 0
while count!=MAX:
    create_account('http://localhost:5000/createAccount')
    login('http://localhost:5000/login')
    create_blog('http://localhost:5000/createBlog',{'token':'token'},'error','error','error')
    count+=1

# cont = int(input())
# if cont!=1: exit()

#create blogs
with open("data.json") as jfile:
    data = json.load(jfile)
for i in range(MAX):
    title,author,content = choice(data['title']),choice(data['author']),choice(data['content'])
    create_blog('http://localhost:5000/createBlog',login_token,title,author,content)
blogs_json = requests.get("http://localhost:5000/fetchBlogs").json()
blogs = blogs_json["data"]


#read random blogs
count = 0
while count!=MAX:
    blogid = choice(blogs)
    requests.get(f"http://localhost:5000/readOne?blogid={blogid}")
    count+=1

#post comments to random blogs
count = 0
comment_data = []
with open("data2.json") as fjson:
    comment_data = json.load(fjson)
while count!=MAX:
    blogid = choice(blogs)
    title,body,author = choice(comment_data["title"]),choice(comment_data["body"]),choice(comment_data["author"])
    data = {"title":title,"body":body,"author":author,"blogID":blogid}
    requests.post(f"http://localhost:5000/createComment?blogid={blogid}",data=data,cookies=login_token)
    count+=1
print("Done with simulation!!")