'''
Script to make POST and GET requests once in every 15 seconds
'''
from random import *
from turtle import title
import requests
import threading
from multiprocessing import Process
import re

MAX = 100
TIME = 3

login_token = None

def setInterval(sec,func,args):
    e = threading.Event()

    while not e.wait(sec): #if timeout of the event happens, it returns False. Till then it return True
        func(args["url"],args['randomization_config'],args['count'],args["params"])

def make_get_request(url,randomization_config,count=0,params = None):
    if randomization_config['bool']:
        url = choice(randomization_config['urls'])

    if not params:
        print("Made request to ",url,count,"number of times")
        requests.get(url=url)
    else:
        requests.get(url=url,params=params)

    if count<MAX:
        setInterval(TIME,make_get_request,{'url':url,'params':params,'count':count+1,'randomization_config':randomization_config})
    else:
        return

def make_post_request(url,count=0):
    print(f"req made to {url} {count} number of times")
    res = requests.post(url,{'username':'qwdqwdqwd', 'password':'3123wdfwef'})
    print("Response of login",res) #use this and set token

    if count < MAX:
        setInterval(TIME,make_post_request(url,count+1))
    else:
        return

def create_blog(url,token,count):
    cookies = {'token':token}
    res = requests.post(url,data={'title':f'Blog {count}','author':'random_author','body':"body of form..dqwdqwddqwdjwqdjojiodwqjiowdjiowqd"},cookies=cookies)
    print("")

    if count < MAX:
        setInterval(TIME,create_blog(url,token,count+1))
    else:
        return

# for varied length of posts and checking time taken to fetch
# can use for response size check and latency check
def createBlog_variedLengths(url,count,length = 500,MAXPOSTS = 10):

    def getRandomString(lengthOfString,s = f'This Blog Has length = {length} This Blog Has length = {length} This Blog Has length = {length}\n'):
        return s * (lengthOfString//len(s))

    res = requests.post(url = "http://localhost:5000/login",data = {'username':'admin','password':'admin'})
    cookie = {'token':res.cookies.get_dict()['token']}

    res = requests.post(url,data={'title':f'Blog {count}','author':'random_author','body':f"{getRandomString(length)}"},cookies=cookie)
    print("")

    if count < MAXPOSTS:
        setInterval(TIME,createBlog_variedLengths(url,count+1,length * 2,MAXPOSTS))
    else:
        return

def getAllBlogs():
    res = requests.get(url='http://localhost:5000/readBlogs',params=None)
    allBlogID = [str(re.findall('id=.*? ',i)[0].split('=')[1][:-1].replace('"','')) for i in [x.group() for x in re.finditer('<button.*?>(.+?)</button>',res.text)]]
    return list(set(allBlogID))

def addCommentsToAllBlogs():
    res = requests.post(url = "http://localhost:5000/login",data = {'username':'admin','password':'admin'})
    cookie = {'token':res.cookies.get_dict()['token']}
    #print(res.cookies.get_dict()['token'])
    allBlogs = getAllBlogs()
    for blogID in allBlogs:
        postToCreateComment(blogID,cookie=cookie,MAX_COUNT=randint(5,20))

def postToCreateComment(blogID,url = 'localhost:5000/createComment',MAX_COUNT = 5,cookie = None):
    count = 0
    if cookie is None:
        res = requests.post(url = "http://localhost:5000/login",data = {'username':'admin','password':'admin'})
        cookie = {'token':res.cookies.get_dict()['token']}
    while count < MAX_COUNT:
        requests.post(url = f"http://{url}?blogID={blogID}",data = {"title":f"Comment title_{count}_{blogID}","body":f"Comment body_{count}_{blogID}\n"*randint(5,100),"author":f"Comment author_{count}_{blogID}","blogID":blogID},cookies=cookie)
        count += 1


randomization_config={'urls':['http://localhost:5000/login','http://localhost:5000/home','http://localhost:5000/readBlogs',],'bool':True}

#p = Process(target=make_get_request,args=(None,randomization_config))
#q = Process(target=make_get_request,args=('http://localhost:5000/readOne?blogid=62977be36b153f5b59a972ec',{'bool':False}))
#r = Process(target=make_post_request,args=('http://localhost:5000/login'))
#
#p.start()
#q.start()
#r.start()
#
#p.join()
#q.join()
#r.join()