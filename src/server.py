from bottle import Bottle, route, run, template
from bottle import HTTPResponse
from bottle import static_file
from multiprocessing import Process
import time
import os
from src.logger import Logger

# This is to mix-in the logger
class Btl(Bottle, Logger):
    pass

application= Btl()

fn = '.api_key'
home = os.path.expanduser('~')

try:
    with open(os.path.join(home, fn)) as f:
        key = ''.join(f.readlines()).replace('\n', '')

except Exception as e:
    exit(-1)

def daemon():
    counter = 3
    while counter > 0:
        time.sleep(1)
        application.logger.debug("Daemon running")
        counter -= 1

@application.route(f'/<api_key>/test')
def client(api_key):
    task = Process(target=daemon)
    task.start()
    return HTTPResponse(body=template('<b>Hello {{api_key}}</b>!', api_key=api_key), status=202)

@application.route(f'/<api_key>/client')
def client(api_key):
    filename = 'client.ovpn'
    return static_file(filename, root=home, download=filename)