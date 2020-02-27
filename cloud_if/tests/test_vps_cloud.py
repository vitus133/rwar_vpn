''' VPS Cloud tests '''
import unittest 
from cloud_if.vps_cloud import VpsCloud

class TestVpsCloud(unittest.TestCase): 
    def setUp(self): 
        self.supported_vendors = ['DigitalOcean']
        self.unsupported_vendor = 'Dummy'
  
    def test_hello(self):         
        for vendor in self.supported_vendors:
            vps = VpsCloud(vendor)
            self.assertEqual(vps.hello(), f'Hello from {vendor}')
  
    # Returns true if the string is stripped and  
    # matches the given output. 
    def test_strip(self):         
        s = 'geeksforgeeks'
        self.assertEqual(s.strip('geek'), 'sforgeeks') 
  
    # Returns true if the string splits and matches 
    # the given output. 
    def test_split(self):         
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world']) 
        with self.assertRaises(TypeError): 
            s.split(2) 
  
if __name__ == '__main__': 
    unittest.main() 
