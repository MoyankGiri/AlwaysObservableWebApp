from prometheus_client import Counter, Histogram
import time
'''
Application level errors
Req / http level errors
'''

APP_ERROR = Counter(
    'app_error_count', #name
    'counts number of errors in application', #desc
    ['app_name','method','endpoint','err_mesg'] #label format
)

def count_error(method_name,endpoint_name,info='default'):
    print(f"Error found in {method_name}/{endpoint_name}")
    APP_ERROR.labels(
        'always_observable',
        method_name,
        endpoint_name,
        info
    ).inc()