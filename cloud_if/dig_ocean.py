'''
Implements information services required for our application
using DigitalOcean REST API
'''
import os
from cloud_if.vps_cloud import VpsCloud


class DigitalOcean(VpsCloud):
    def __init__(self, config):
        self.config = config
        self.droplets = []
        self.key = self._read_api_key()
    
    def _read_api_key(self):
        fn = self.config.get('DigitalOcean API key file')
        home = os.path.expanduser('~')
        try:
            with open(os.path.join(home, fn)) as f:
                return ''.join(f.readlines()).replace('\n', '')
        except Exception as e:
            return None

    
    def hello(self):
        return "Hello from DigitalOcean"
    
    def check_secrets(self)->bool:
        return self.key != None
    
    def get_secrets(self)->dict:
        return {'API key': self.key}
    
    def save_secrets(self, secrets:dict)->bool:
        key = secrets.get('API key')
        fn = self.config.get('DigitalOcean API key file')
        home = os.path.expanduser('~')
        try:
            with open(os.path.join(home, fn), 'w') as f:
                f.write(key)
                return True
        except Exception as e:
            return False