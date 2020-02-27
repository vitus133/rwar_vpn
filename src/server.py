from bottle import Bottle, route, run, template
from bottle import HTTPResponse
from threading import Thread
import time
import os

application= Bottle()
fn = '.api_key'
home = os.path.expanduser('~')
try:
    with open(os.path.join(home, fn)) as f:
        key = ''.join(f.readlines()).replace('\n', '')
        
except Exception as e:
    exit(-1)

def daemon_thread():
    counter = 3
    while counter > 0:
        time.sleep(1)
        print("Daemon thread running")
        counter -= 1

@application.route(f'/<api_key>/client')
def client(api_key):
    print(api_key, key)
    task_thread = Thread(target=daemon_thread)
    task_thread.setDaemon(True) 
    task_thread.start()
    return HTTPResponse(body=template('<b>Hello {{api_key}}</b>!', api_key=api_key), status=202)
    

