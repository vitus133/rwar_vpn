'''
VpsCloud class implements information services that 
we implement via the cloud provider API.
'''
from cloud_if.config import config

class VpsCloud():
    # A list of supported VPS vendors
    vendors = [
        'DigitalOcean'
    ]
    # Operation status
    op_status = [
        'Success', 'Failure', 'Failure and need cleanup'
    ]

    def __init__(self, vendor:str):
        if vendor not in VpsCloud.vendors:
            raise NameError(f"{vendor} is not supported")
        elif vendor == 'DigitalOcean':
            from cloud_if.dig_ocean import DigitalOcean as vps
            self.vps = vps(config)

    def save_secrets(self, secrets:dict)->bool:
        return self.vps.save_secrets(secrets)

    def get_secrets(self)->dict:
        return self.vps.get_secrets()
    
    # Returns True if there are secrets stored, otherwise False
    def check_secrets(self)->bool:
        return self.vps.check_secrets()

    


if __name__ == '__main__':
    cloud = VpsCloud('DigitalOcean')
    cloud.hello()