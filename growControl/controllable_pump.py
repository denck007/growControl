import os
import time
import datetime
try:
    import RPi.GPIO as GPIO
except:
    print("Controllable_Pump: Unable to import raspberry pi specific modules" +\
             "\tWill only be able to run with 'gpio_pin=None'")

class Controllable_Pump:
    '''
    Defines a peristaltic pump and the control of it
    '''

    def __init__(self,gpio_pin,verbose=False):
        '''
        Initialize a pump for control
        '''
        self.verbose = verbose
        self.gpio_pin = gpio_pin

        # The logic is a little weird. Setting the pin to high
        #  will turn the pump off, and setting to low will turn
        #  will turn the pump on when using a relay that is normally
        #  open. When the wire from the pin to the relay is removed
        #  the pump will stay off. 
        self._turn_pump_off_gpio_value = 1 # 1 = GPIO.HIGH
        self._turn_pump_on_gpio_value = 0 # 0 = GPIO.LOW    
        
        if self.gpio_pin is not None:
            self._initialize_gpio()        
        else:
            self._initialize_gpio_mock()
        
    def _initialize_gpio(self):
        '''
        Configure the GPIO for the pump
        '''

        self._pump_on = self._pump_on_real
        self._pump_off = self._pump_off_real
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio_pin, GPIO.OUT)
        GPIO.output(self.gpio_pin,self._turn_pump_off_gpio_value)

    def cleanup(self):
        '''
        Reset the GPIO
        '''
        if self.verbose:
            print("Cleaning up gpio pin {}".format(self.gpio_pin))
        if self.gpio_pin is not None:
            GPIO.cleanup(self.gpio_pin)

    def _pump_on_real(self):
        '''
        Turn the pump on using the real GPIO
        '''
        if self.verbose:
            print("{:.4f} turning pump on".format(time.time()))
        GPIO.output(self.gpio_pin,self._turn_pump_on_gpio_value)

    def _pump_off_real(self):
        '''
        Turn the pump off using the real GPIO
        '''
        if self.verbose:
            print("{:.4f} turning pump off".format(time.time()))
        GPIO.output(self.gpio_pin,self._turn_pump_off_gpio_value)

    def _initialize_gpio_mock(self):
        '''
        Initialize the controllable pump when GPIO is not availible
        IE when not running on a raspberry pi
        '''
        self._pump_on = self._pump_on_mock
        self._pump_off = self._pump_off_mock

    def _pump_on_mock(self):
        '''
        Turn the pump on using the mock interface for testing
        '''
        if self.verbose:
            print("{:.4f} turning pump on".format(time.time()))

    def _pump_off_mock(self):
        '''
        Turn the pump off using the mock interface for testing
        '''
        if self.verbose:
            print("{:.4f} turning pump off in _pump_off_mock".format(time.time()))

    def __call__(self,time_on):
        '''
        Turn the pump on for time_on seconds
        '''
        self._pump_on()
        time.sleep(time_on)
        self._pump_off()
        
if __name__ == "__main__":
    gpio_pin = 12
    try:
        p = Controllable_Pump(gpio_pin=gpio_pin,verbose=True)
        time.sleep(2)

        for ii in range(3):
            p(1)
            time.sleep(1)
    except:
        print("Exiting Controllable_Pump")
    finally:
        p.cleanup()

