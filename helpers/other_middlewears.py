from prometheus_client import Counter, Histogram
import time
'''
Application level errors
Req / http level errors
'''
BLOG_LATENCY = Histogram(
    'blog_latency', #name
    ' latencies of vaious blogs while getting them from database', #desc
    ['app_name','blog_id','blog_name'] #labe; format
)

def measure_blog_latency(duration,blog_id,title):
    BLOG_LATENCY.labels(
        'always_observable',
        blog_id   ,
        title
    ).observe(duration)
