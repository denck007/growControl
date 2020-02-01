import unittest     
import time

from growControl import Sensor

class test_Sensor(unittest.TestCase):
    '''
    Test the Sensor base object
    '''

    def test_update(self):
        '''
        Basic update function
        '''
        params = {"name":"test_object1",
                    "time_warmup":1,
                    "time_run_every":1,
                    "interface":{}}
        parent= "Test Parent"
        
        s = Sensor(params,parent)

        result = s()

