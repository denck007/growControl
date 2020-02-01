
import os
import time
import datetime

class Pump:
    '''
    Defines a peristaltic pump and the control of it
    '''

    def __init__(self,gpio_address):
        '''
        Initialize a pump for control
        '''

        self.gpio_address = gpio_address
    
        self._initialize_gpio()
        
    def _initialize_gpio(self):
        '''
        Configure the GPIO for the pump
        '''
        pass

    def _pump_on(self):
        '''
        Turn the pump on
        '''
        print("{:.4f} turning pump on".format(time.time()))

    def _pump_off(self):
        '''
        Turn the pump off
        '''
        print("{:.4f} turning pump off".format(time.time()))

    def __call__(self,time_on):
        '''
        Turn the pump on for time_on seconds
        '''
        self._pump_on()
        time.sleep(time_on)
        self._pump_off()
        
if __name__ == "__main__":
    p = Pump()

    for ii in range(10):
        p(.1)

        


    