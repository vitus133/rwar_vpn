'''
VpsCloud class implements information services that 
we implement via the cloud provider API.
'''
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
            self.vps = vps()

    def hello(self):
        return self.vps.hello()

    def add_secrets(self, vendor:str, secrets:dict)->op_status:
        pass
    


if __name__ == '__main__':
    cloud = VpsCloud('DigitalOcean')
    cloud.hello()