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
    # data = user_info.json()
    # print(json.dumps(data, indent=2))
    assert(user_info.status_code == 200)

    rsp = vps.deploy_droplet()
    print(rsp.status_code)
    create_rsp = rsp.json()
    print(json.dumps(create_rsp, indent=2))
    assert(rsp.status_code == 202)


