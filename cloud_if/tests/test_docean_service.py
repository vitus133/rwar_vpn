'''
This module tests DigitalOcean service directly
'''
import json
from cloud_if.dig_ocean import DigitalOcean
from cloud_if.config import config



if __name__ == '__main__': 
    vps = DigitalOcean(config)
    assert(vps.check_secrets())
    user_info = vps.get_info()
    print(user_info)
    print(f"Continue? [y/N]")
    if input() != 'y':
        exit(0)
    
    if not user_info.get('droplets').get('total'):
        print(f"Deploy? [y/N]")
        if input() == 'y':
            # deploy droplet if there is none
            rsp = vps.deploy_droplet()
            print(rsp.status_code)
            create_rsp = rsp.json()
            print(json.dumps(create_rsp, indent=2))
            assert(rsp.status_code == 202)
            vps.block_until_active()
            user_info = vps.get_info()
            print(vps.droplet)
            '''
            ipv4 = 
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
            '''




    print(f"Delete? [y/N]")
    if input() != 'y':
        exit(0)
    rsp = vps.clean_all()
    print(rsp.status_code)
    print(rsp.headers)    


