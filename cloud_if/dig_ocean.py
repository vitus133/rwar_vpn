import os
import requests
from urllib3.exceptions import InsecureRequestWarning

class DigitalOcean():
    '''
    Implements information services required for our application
    using DigitalOcean REST API
    '''
    def __init__(self, config:dict):
        '''
        DigitalOcean class init.
        '''
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
        self.config = config.get('DigitalOcean')
        if not self.config:
            raise KeyError('DigitalOcean config is invalid')
        self.droplets = []
        self.key = self._read_api_key()
    
    def _read_api_key(self):
        # Returns API key if exists, otherwise None
        fn = self.config.get('API key file')
        home = os.path.expanduser('~')
        try:
            with open(os.path.join(home, fn)) as f:
                return ''.join(f.readlines()).replace('\n', '')
        except Exception as e:
            return None
    
    def _get_headers(self):
        # Preparing HTTP headers used in every request
        return {'Authorization': f'Bearer {self.key}',
                'Content-Type': 'application/json'}

    def check_secrets(self)->bool:
        # Checks for existence of API key
        return self.key != None
    
    def get_secrets(self)->dict:
        # Returns the stored API key
        return {'API key': self.key}
    
    def save_secrets(self, secrets:dict)->bool:
        # Stores API key on file system
        key = secrets.get('API key')
        fn = self.config.get('API key file')
        home = os.path.expanduser('~')
        try:
            with open(os.path.join(home, fn), 'w') as f:
                f.write(key)
                return True
        except Exception as e:
            return False
    
    def _api_get(self, endpoint:str):
        base_url = self.config.get('base_url')
        headers = self._get_headers()
        try:
            response = requests.get(url=f'{base_url}/{endpoint}',
                headers=headers)
        except requests.exceptions.HTTPError as e:
            print(e)
        return response

    def get_user_info(self):
        '''
        Returns user info, for example:
        {
        "account": {
            "droplet_limit": 10,
            "floating_ip_limit": 3,
            "volume_limit": 10,
            "email": "abc@de.com",
            "uuid": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
            "email_verified": true,
            "status": "active",
            "status_message": ""
            }
        }
        '''
        return self._api_get('account')

    
