'''
Script to make POST and GET requests once in every 15 seconds
'''
import requests
import threading
from multiprocessing import Process

MAX = 100
TIME = 3

def setInterval(sec,func,args):
    e = threading.Event()

    while not e.wait(sec): #if timeout of the event happens, it returns False. Till then it return True
        func(args["url"],args['count'],args["params"])

def make_get_request(url,count=0,params = None):
    if not params:
        print("Made request to ",url,count,"number of times")
        requests.get(url=url)
    else:
        requests.get(url=url,params=params)

    if count<MAX:
        setInterval(TIME,make_get_request,{'url':url,'params':params,'count':count+1})
    else:
        return


p = Process(target=make_get_request,args=('http://192.168.29.17:5000/home',))
q = Process(target=make_get_request,args=('http://192.168.29.17:5000/readOne?blogid=62977be36b153f5b59a972ec',))

p.start()
q.start()

p.join()
q.join()