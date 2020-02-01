
import time
import datetime
import os

from control_pump import Pump


class Controller_ph_pump:
    ''' 
    Uses to pumps to control the ph of a system
    '''

    def __init__(self,sensor_ph):
        '''
        Turns on ph up and down pumps based on the current ph of sensor_ph
        '''

        self.sensor_ph = sensor_ph

        self.ph_min = 5.8
        self.ph_max = 6.2
        self.control_every = 5 # seconds, minimum time since last control to issue a control command
        self.warmup_time = 1 # seconds, minimum time after startup to issue first control commmand

        self.pump_down = Pump(gpio_address=-1)
        self.pump_up = Pump(gpio_address=-2)

        self.last_control = time.time() + self.warmup_time

    def __call__(self):
        '''
        Execute a control command based on the current sensor_ph value, and time since last control
        ''' 
        current_time = time.time()
        if current_time - self.control_every < self.last_control:
            return 
        
        if self.sensor_ph.ph_avg > self.ph_max:
            print("ph low {:.1f}s since last control".format(current_time-self.last_control))
            self.pump_down(.1)
            self.last_control = current_time
        elif self.sensor_ph.ph_avg < self.ph_min:
            print("ph high {:.1f}s since last control".format(current_time-self.last_control))
            self.pump_up(.1)
            self.last_control = current_time()
        

if __name__ == "__main__":
    from sensor_ph import Sensor_ph
    
    sensor_ph = Sensor_ph(csv="/home/neil/growControl/testing_input_files/voltages.csv")
    controller = Controller_ph_pump(sensor_ph)

    for ii in range(20):
        print()
        sensor_ph()
        controller()
        time.sleep(.5)