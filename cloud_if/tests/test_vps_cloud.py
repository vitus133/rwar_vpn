''' VPS Cloud tests '''
import unittest
import os
from unittest.mock import Mock
from cloud_if.vps_cloud import VpsCloud
from cloud_if.config import config

class TestDigitalOceanSecrets(unittest.TestCase):
    def setUp(self):
        print("calling setup in TestDigitalOceanSecrets")
        self.temp_key = '445566'
        docean_secrets_f = config.get('DigitalOcean API key file')
        home_dir = os.path.expanduser('~')
        self.docean_secrets_f = os.path.join(home_dir, docean_secrets_f)
        if os.path.isfile(self.docean_secrets_f):
            os.replace(self.docean_secrets_f, f"{self.docean_secrets_f}.orig")
        vps = VpsCloud('DigitalOcean')
        self.assertTrue(vps.save_secrets({'API key': self.temp_key}))

    def tearDown(self):
        print("calling tearDown in TestDigitalOceanSecrets")
        if os.path.isfile(f"{self.docean_secrets_f}.orig"):
            os.replace(f"{self.docean_secrets_f}.orig", self.docean_secrets_f)
    
    def test_digocean_no_api_key(self):
        from cloud_if.dig_ocean import DigitalOcean
        cfg = {'DigitalOcean API key file': '.digitalocean000000000000000'}
        vps = DigitalOcean(cfg)
        self.assertEqual(vps.key, None)
        cfg = {}
        vps = DigitalOcean(cfg)
        self.assertEqual(vps.key, None)
        

    def test_digocean_get_secrets_format(self):
        vps = VpsCloud('DigitalOcean')
        secrets = vps.get_secrets()
        self.assertIn('API key', secrets.keys())
        
    def test_digo_r_api_key(self):
        vps = VpsCloud('DigitalOcean')
        self.assertEqual(vps.get_secrets().get('API key'), self.temp_key)



class TestVpsCloud(unittest.TestCase): 
    def setUp(self): 
        self.supported_vendors = ['DigitalOcean']
        self.unsupported_vendor = 'Dummy'
    
    def tearDown(self):
        pass

    # Tests it can work with all supported vendors
    def test_hello(self):         
        for vendor in self.supported_vendors:
            vps = VpsCloud(vendor)
  
    # Tests unsupported vendors throw exception
    def test_unsupported(self):         
        with self.assertRaises(NameError): 
            vps = VpsCloud(self.unsupported_vendor)
    
if __name__ == '__main__': 
    unittest.main() 
