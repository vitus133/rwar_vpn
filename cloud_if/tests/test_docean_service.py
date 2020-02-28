'''
This module tests DigitalOcean service directly
'''
import json
from cloud_if.dig_ocean import DigitalOcean
from cloud_if.config import config


if __name__ == '__main__': 
    vps = DigitalOcean(config)
    assert(vps.check_secrets())
    user_info = vps.get_user_info()
    assert(user_info.status_code == 200)
    data = user_info.json()
    print(json.dumps(data, indent=2))
    vps.deploy_droplet()


