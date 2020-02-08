from unittest import TestCase
import tempfile
import os
import sys
import time

from growControl import Controllable_Pump

class test_Controllable_Pump(TestCase):
    '''
    Test cases for the Controllable_Pump class
    '''

    def assertFloatsClose(self,a,b,eps=1e-6):
        '''
        Asserts that a and b are within eps of eachother
        '''
        delta = abs(a-b)
        self.assertTrue(delta < eps,msg="Floats {} and {} are not within {} of eachother.".format(a,b,eps))

    def test_Controllable_Pump(self):
        '''
        '''
        cp = Controllable_Pump(gpio_pin=None)

        dts = [0.1,0.15,0.2]
        for dt in dts:
            start_time = time.time()
            cp(dt)
            end_time = time.time()
            self.assertFloatsClose(start_time+dt,end_time,eps=dt/100.) # get within 1% 

    def test_controllable_pump_real_output(self):
        '''
        Verifies:
            * Recorded time is correct
        '''
        if os.uname().machine != "armv6l":
            print("test_controllable_pump_real_output only works on the raspberrypi!")
            return

        try:
            cp = Controllable_Pump(gpio_pin=12)    

            dts = [0.5,0.75,1.0]
            for dt in dts:
                start_time = time.time()
                cp(dt)
                end_time = time.time()
                self.assertFloatsClose(start_time+dt,end_time,eps=dt/100.*5) # get within 5% 
                time.sleep(.05)
        finally:
            cp.cleanup()
