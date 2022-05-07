from flask import request
from prometheus_client import Counter, Histogram
import time

REQ_COUNT = Counter(
    'request_count', #name
    'req counter', #desc
    ['app_name','method','endpoint','http_status'] #label format
)

REQ_LATENCY = Histogram(
    'request_latency_in_sec',
    'latency of request measured in seconds',
    ['app_name','endpoint']
)

def record_req_data(response):
    # print("Counting record ie record_count++")

    #inc counter for specific label
    REQ_COUNT.labels(
        'always_observable_aws',
        request.method,
        request.path,
        response.status_code
    ).inc()
    return response

def start_timer():
    # print("timer started!")
    request.begin_time = time.time()

def stop_timer(response):
    # print("timer closed!")

    elapsed_time = time.time() - request.begin_time
    #save metric in label
    REQ_LATENCY.labels(
        'always_observable_aws',
        request.path
    ).observe(elapsed_time)
    return response

def setup_metrics(app):
    # print("Setting up middle wear!")

    #start timer on the request
    app.before_request(start_timer)

    #after req is made,call the middle wear
    app.after_request(record_req_data)

    #after req, stop timer
    app.after_request(stop_timer)