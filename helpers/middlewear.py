from flask import request
from prometheus_client import Counter, Histogram
import time

CLICK_COUNT = Counter(
    'click_count',
    'measure popularity of blog using click through rate',
    ['app_name','blog_id']
)

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

RES_SIZE = Histogram(
    'response_size',
    'size of response body',
    ['app_name']
)

def res_size(response):
    size = None

    try:
        size = len(response.data)
        print("RESPONSE---->",size)

        RES_SIZE.labels(
            'always_observable',
        ).observe(size)
        
    except Exception as e:
        print(e)
    return response

def popularity_handle():
    print("***********START***************")
    print(request.args.get('blogid'))
    blogID = request.args.get('blogid')
    if blogID:
        CLICK_COUNT.labels(
            'always_observable',
            request.args.get('blogid')
        ).inc()
    else:
        print("No rec created!")
    print("***********END***************")

def record_req_data(response):
    # print("Counting record ie record_count++")

    #inc counter for specific label
    REQ_COUNT.labels(
        'always_observable_aws',
        request.method, #GET,PUT,POST etc
        request.path,
        response.status_code
    ).inc()
    return response

def start_timer():
    #print("timer started!")
    request.begin_time = time.time()

def stop_timer(response):
    #print("timer closed!")

    elapsed_time = time.time() - request.begin_time
    #print("Elapsed time",elapsed_time)

    #save metric in label
    REQ_LATENCY.labels(
        'always_observable_aws',
        request.path
    ).observe(elapsed_time)

    return response

def setup_metrics(app):
    # print("Setting up middle wear!")

    app.before_request(popularity_handle)

    #register start_timer() to run before the request
    app.before_request(start_timer)

    #register record_req_data() to run after request
    app.after_request(record_req_data)

    #after req, stop timer
    app.after_request(stop_timer)

    app.after_request(res_size)