import os
import requests
import secrets
import json
import time
from urllib3.exceptions import InsecureRequestWarning
from src.logger import Logger


class DigitalOcean(Logger):
    '''
    Implements information services required for our application
    using DigitalOcean REST API
    '''
    def __init__(self, config: dict):
        '''
        DigitalOcean class init.
        '''
        # We only care about transport encryption, so we disable this warning
        requests.packages.urllib3.disable_warnings(
            category=InsecureRequestWarning)
        self.config = config.get('DigitalOcean')
        self.common_config = config.get('Common')
        if not self.config:
            raise KeyError('DigitalOcean config is invalid')
        self.droplet = None
        self.home = os.path.expanduser('~')
        self.key = self._read_api_key()
        self.ssh_fp = self._read_ssh_fingerprint()
        self.vm_name = self.common_config.get("vm_name", "rwarvpn")
        self.region = self.config.get("region", "nyc1")
        self.size = self.config.get("size", "s-1vcpu-1gb")
        self.image = self.config.get("image", "centos-8-x64")
        self.backups = self.config.get("backups", False)
        self.ipv6 = self.config.get("ipv6", False)
        self.private_networking = self.config.get("private_networking", None)
        self.volumes = self.config.get("volumes", None)
        self.user_script_url = self.common_config.get("user_script_url", None)
        self.tags = self.common_config.get('tags', 
            ['bh5QpzZHqeUBpaWLI4bnYzM3GFEdcJQ1sNXTNeazShEDZOY6'])
        self.web_api_key = secrets.token_urlsafe(24)
        self.user_data = (
            f"#!/bin/bash\n"
            f"echo {self.web_api_key} > /root/.api_key && "
            f"/usr/bin/curl {self.user_script_url} | /bin/bash")

    def deploy_droplet(self):
        self.logger.info("Deploy droplet, starting")
        data = {
            "name": self.vm_name,
            "region": self.region,
            "size": self.size,
            "image": self.image,
            "ssh_keys": [self.ssh_fp],
            "backups": self.backups,
            "ipv6": self.ipv6,
            "user_data": self.user_data,
            "private_networking": self.private_networking,
            "volumes": self.volumes,
            "tags": self.tags}
        rsp = self._api_post('droplets', data)
        if rsp.status_code == 202:
            j_rsp = rsp.json()
            droplet_id = j_rsp.get('droplet').get('id')
            droplet_data = {'droplet_id': droplet_id, 'api key': self.web_api_key}
            self.droplet = droplet_data
        return rsp
    
    def block_until_active(self, timeout=60, sleep=10) -> bool:
        if not self.droplet:
            self.logger.error("There is no droplet to wait for")
            return False
        dr_status = ''
        time_spent = 0
        while time_spent < timeout:
            droplet_id = self.droplet.get('droplet_id')
            endpoint = f"/droplets/{droplet_id}"
            rsp = self._api_get(endpoint)
            if rsp.status_code == 200:
                j_rsp = rsp.json()
                dr_status = j_rsp.get('droplet').get('status')
                if dr_status == 'active':
                    ipv4 = j_rsp.get('droplet').get('networks').get('v4')[0].get('ip_address')
                    if self.droplet:
                        self.droplet['ipv4'] = ipv4
                    self.logger.debug(f"Droplet {droplet_id} is active")
                    return True
                msg = (f"Waiting for droplet"
                    f" to become active...{time.time()}")
                self.logger.debug(msg)
                time_spent += sleep
                time.sleep(sleep)                
            else:
                msg = (f"Droplet get by ID failed:"
                    f" {rsp.status_code}, {rsp.text}")
                self.logger.error(msg)
                return False
        self.logger.error(f"Droplet {droplet_id} activation check"
            f" exited on timeout")      
        return false

    def _rd_single_str_file(self, file_path):
        # Reads a file into a single string
        try:
            with open(file_path) as f:
                return ''.join(f.readlines()).replace('\n', '')
        except Exception as e:
            self.logger.exception(e)
            return None

    def _wr_single_str_file(self, file_path, info: str) -> bool:
        # Writes / replace a single string into a file
        # Returns bool Success (False on failure)
        try:
            with open(file_path, 'w') as f:
                f.write(info)
                return True
        except Exception as e:
            self.logger.exception(e)
            return False

    def _read_ssh_fingerprint(self):
        # Returns SSH fingerprint if exists, otherwise None
        try:
            fn = os.path.join(self.home, self.config.get('ssh'))
            return self._rd_single_str_file(fn)
        except Exception as e:
            self.logger.exception(f"SSH fingerprint is not configured, {e}")
            return None

    def _wr_ssh_fingerprint(self, info: str) -> bool:
        # Writes SSH fingerprint, returns bool status (False on failure)
        try:
            fn = os.path.join(self.home, self.config.get('ssh'))
            return self._wr_single_str_file(fn, info)
        except TypeError as e:
            self.logger.info(f"SSH fingerprint is not configured, {e}")
            return False
        except Exception as e:
            self.logger.exception(f"Failed to write {fn}, {e}")

    def _read_api_key(self):
        # Returns API key if exists, otherwise None
        fn = os.path.join(self.home, self.config.get('API key file'))
        return self._rd_single_str_file(fn)

    def _get_headers(self):
        # Preparing HTTP headers used in every request
        return {'Authorization': f'Bearer {self.key}',
                'Content-Type': 'application/json'}

    def check_secrets(self) -> bool:
        # Checks for existence of API key
        return self.key is not None

    def get_secrets(self) -> dict:
        # Returns the stored API key
        return {'API key': self.key}

    def save_secrets(self, secrets: dict) -> bool:
        # Stores API key on file system
        key = secrets.get('API key')
        fn = os.path.join(self.home, self.config.get('API key file'))
        return self._wr_single_str_file(fn, key)

    def _api_get(self, endpoint: str):
        base_url = self.config.get('base_url')
        headers = self._get_headers()
        try:
            response = requests.get(url=f'{base_url}/{endpoint}',
                                    headers=headers)
        except requests.exceptions.HTTPError as e:
            print(e)
        return response

    def _api_post(self, endpoint: str, data: dict):
        base_url = self.config.get('base_url')
        headers = self._get_headers()
        try:
            response = requests.post(url=f'{base_url}/{endpoint}',
                                    headers=headers,
                                    data=json.dumps(data))
        except requests.exceptions.HTTPError as e:
            self.logger.exception(e)
        return response

    def _api_delete(self, endpoint: str):
        base_url = self.config.get('base_url')
        headers = self._get_headers()
        try:
            response = requests.delete(url=f'{base_url}/{endpoint}',
                                    headers=headers)
        except requests.exceptions.HTTPError as e:
            self.logger.exception(e)
        return response

    def get_info(self):
        rsp = self._api_get('account')
        if rsp.status_code == 200:
            j_rsp = rsp.json()
            ret = {
                "status_message": j_rsp.get("status_message"),
            }
            tag = self.tags[0]
            endpoint = f"/droplets/?tag_name={tag}"
            rsp = self._api_get(endpoint)
            if rsp.status_code == 200:
                j_rsp = rsp.json()
                self.logger.debug(json.dumps(j_rsp, indent=2))
                ret['droplets'] = {}
                ret['droplets']['total'] = j_rsp.get('meta').get('total')
                ret['droplets']['ids'] = \
                    [i.get('id') for i in j_rsp.get('droplets')]
            else:
                ret['error'] = {}
                ret['error']['code'] = rsp.status_code
                ret['error']['text'] = rsp.text
            return ret
        else:
            self.logger.error(rsp.status_code, rsp.text)
            return None

    def clean_all(self):
        tag = self.tags[0]
        endpoint = f"/droplets/?tag_name={tag}"
        return self._api_delete(endpoint)