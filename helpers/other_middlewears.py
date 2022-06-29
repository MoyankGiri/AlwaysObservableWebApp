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

BLOG_COMMENTS = Counter(
    'blog_comment_counter',
    'blog with most comments',
    ['app_name','blog_id']
)

def measure_blog_latency(duration,blog_id,title):
    BLOG_LATENCY.labels(
        'always_observable',
        blog_id   ,
        title
    ).observe(duration)

def increment_blog_comments(blog_id):
    BLOG_COMMENTS.labels(
        'always_observable',
        blog_id
    ).inc()
