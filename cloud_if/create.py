import requests
import json
import sys
import os
import secrets
import time
from urllib3.exceptions import InsecureRequestWarning

def get_access_key()->str:
    fn = '.digitalocean'
    home = os.path.expanduser('~')
    try:
        with open(os.path.join(home, fn)) as f:
            key = ''.join(f.readlines()).replace('\n', '')
            return key
    except Exception as e:
        return None


def get_ssh_fingerprints()-> list:
    fn = '.digitalocean_ssh_keys'
    home = os.path.expanduser('~')
    try:
        with open(os.path.join(home, fn)) as f:
            keys = f.readlines()
            return [i.replace('\n', '') for i in keys]
    except Exception as e:
        return []

svr_api_key = secrets.token_urlsafe(24)
user_script_url = 'https://raw.githubusercontent.com/vitus133/rwar_vpn/master/deploy.sh'

def deploy_droplet()->requests.Response:
    data = {
    "name": "vg-test",
    "region": "nyc1",
    "size": "s-1vcpu-1gb",
    "image": "centos-8-x64",
    "ssh_keys": get_ssh_fingerprints(),
    "backups": False,
    "ipv6": True,
    "user_data": f"#!/bin/bash\necho {svr_api_key} > /root/.api_key && /usr/bin/curl {user_script_url} | /bin/bash",
    "private_networking": None,
    "volumes": None,
    "tags": [
        "standard"
    ]
    }

    api_key = get_access_key()
    try:
        response = requests.post(url=f'https://api.digitalocean.com/v2/droplets',
                                 headers={'Authorization': f'Bearer {api_key}',
                                          'Content-Type': 'application/json'},
                                data=json.dumps(data))
    except requests.exceptions.HTTPError as e:
        print(e)
    return(response)


def get_droplet_status(id):
    api_key = get_access_key()
    try:
        response = requests.get(url=f'https://api.digitalocean.com/v2/droplets/{id}',
                                 headers={'Authorization': f'Bearer {api_key}',
                                          'Content-Type': 'application/json'})
    except requests.exceptions.HTTPError as e:
        print(e)

    return(response)


if __name__ == "__main__":
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
    print(svr_api_key)
    rsp = deploy_droplet()
    assert(rsp.status_code == 202)
    create_rsp = rsp.json()
    # print(json.dumps(create_rsp, indent=2))
    droplet_id = create_rsp.get('droplet').get('id')
    print(f"Successfully created droplet with ID {droplet_id}")
    dr_status = ''
    while dr_status != 'active':
        print(f"Waiting for droplet to become active...")
        time.sleep(10)
        rsp = get_droplet_status(droplet_id)
        assert(rsp.status_code == 200)
        status_rsp = rsp.json()
        dr_status = status_rsp.get('droplet').get('status')
        # print(json.dumps(status_rsp, indent=2))
    if dr_status == 'active':
        ipv4 = status_rsp.get('droplet').get('networks').get('v4')[0].get('ip_address')
        print(f"Droplet is active, ip: {ipv4}")

    status_code = ''
    sleep_time = 10
    delay_time = 120
    while status_code != 202 and delay_time > 0:
        print("Waiting for web server to get installed and up")
        time.sleep(sleep_time)
        try:
            delay_time -= sleep_time
            rsp = requests.get(url=f"https://{ipv4}:4443/hello/test", verify=False)
            status_code = rsp.status_code
            print(status_code)
        except Exception as e:
            pass
            #print(e)
    if delay_time <= 0:
        print("Setup failed")
        exit(1)
    print("Setup succeeded")
    exit(0)
    

    
    
