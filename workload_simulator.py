'''
Script to make POST and GET requests once in every 15 seconds
'''
from random import *
import requests
import threading
from multiprocessing import Process

MAX = 100
TIME = 3

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
    requests.post(url,{'username':'qwdqwdqwd', 'password':'3123wdfwef'})

    if count < MAX:
        setInterval(TIME,make_post_request(url,count+1))
    else:
        return

randomization_config={'urls':['http://localhost:5000/login','http://localhost:5000/home','http://localhost:5000/readBlogs',],'bool':True}

p = Process(target=make_get_request,args=(None,randomization_config))
q = Process(target=make_get_request,args=('http://localhost:5000/readOne?blogid=62977be36b153f5b59a972ec',{'bool':False}))
r = Process(target=make_post_request,args=('http://localhost:5000/login'))

p.start()
q.start()
r.start()

p.join()
q.join()
r.join()