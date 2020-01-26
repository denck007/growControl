import unittest     
import time

from growControl import GrowObject

class Test_GrowObject(unittest.TestCase):

    def test_init(self):
        '''
        Verify that all parameters passed in are set
        Note this does not test the interface code at all!
        '''
        params = {"name":"test_object1",
                    "time_warmup":1,
                    "time_run_every":1,
                    "interface":{}}
        parent= "Test Parent"
        go = GrowObject(params=params,parent=parent)

        self.assertEqual(go.name,params["name"],"name not assigned correctly")
        self.assertEqual(go.time_warmup,params["time_warmup"],"time_warmup not assigned correctly")
        self.assertEqual(go.time_run_every,params["time_run_every"],"time_run_every not assigned correctly")
        self.assertEqual(go.interface,None,"interface should be None")
        self.assertEqual(go.parent,parent,"parent not assigned correctly")
        self.assertAlmostEqual(go.time_previous,time.time(),places=2, msg="time_previous should be initialized to when the GrowObject is instatiated")

    def test_init_with_defaults(self):
        '''
        Test that all of the defaults are set correctly
        '''
        params = {"name":"test_object1"}
        parent= None
        go = GrowObject(params=params,parent=parent)

        self.assertEqual(go.name,params["name"],"name not assigned correctly")
        self.assertEqual(go.time_warmup,0,"time_warmup not assigned correctly")
        self.assertEqual(go.time_run_every,0,"time_run_every not assigned correctly")
        self.assertEqual(go.interface,None,"interface should be None")
        self.assertEqual(go.parent,None,"parent should be none")
        self.assertAlmostEqual(go.time_previous,time.time(),places=2, msg="time_previous should be initialized to when the GrowObject is instatiated")
    
