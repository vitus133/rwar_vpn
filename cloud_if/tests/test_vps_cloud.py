''' VPS Cloud tests '''
import unittest 
from cloud_if.vps_cloud import VpsCloud

class TestVpsCloud(unittest.TestCase): 
    def setUp(self): 
        self.supported_vendors = ['DigitalOcean']
        self.unsupported_vendor = 'Dummy'
  
    # Tests it can work with all supported vendors
    def test_hello(self):         
        for vendor in self.supported_vendors:
            vps = VpsCloud(vendor)
            self.assertEqual(vps.hello(), f'Hello from {vendor}')
  
    # Tetss unsupported vendors throw exception
    def test_unsupported(self):         
        with self.assertRaises(NameError): 
            vps = VpsCloud(self.unsupported_vendor) 
  
if __name__ == '__main__': 
    unittest.main() 
