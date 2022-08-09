import random
import requests
import threading
from multiprocessing import Process

MAX_COUNT = 5

def postToCreateComment(blogID = "62aec30e8960cd8f6ac14221",url = 'localhost:5000/createComment'):
    count = 0
    
    requests.post(url = "http://localhost:5000/login",data = {'username':'admin','password':'admin'})
    while count < MAX_COUNT:
        print("HERE")
        requests.post(url = f"http://{url}?blogID={blogID}",data = {"title":f"title_{count}","body":f"body_{count}","author":f"author_{count}","blogID":blogID})
        count += 1

postToCreateComment()

