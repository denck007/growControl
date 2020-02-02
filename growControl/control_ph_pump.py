
import time
import datetime
import os

class Controller_ph_Pump:
    ''' 
    Uses to pumps to control the ph of a system
    '''

    def __init__(self,sensor_ph, pump_ph_up, pump_ph_down, output_file, ml_per_s=1.0, dispense_volume=3.0, ph_min=5.8, ph_max=6.2, control_every=30*60, warmup_time=10*60, verbose=False):
        '''
        Turns on ph up and down pumps based on the current ph of sensor_ph
        
        sensor_ph: The sensor to read ph_avg from to control by
        pump_ph_up: Instance of Controllable_Pump that is connected to ph up fluid
        pump_ph_down: Instance of Controllable_Pump that is connected to ph down fluid
        output_file: File to store the output data to

        ml_per_s: Float: The number of ml of fluid that are dispensed with each second of pump time
        dispense_volume: Float: The volume in ml to dispense with each control cycle
        ph_min: Float, If the ph on sensor_ph.ph_avg is below this value and it has been control_every seconds 
            since the last control action, activate the ph_up pump
        ph_max: Float, If the ph on sensor_ph.ph_avg is above this value and it has been control_every seconds 
            since the last control action, activate the ph_down pump
        control_every: Float: Minimum number of seconds must pass between each control action
        warmup_time: Float: Minimum number of seconds after the controller is instantiated before a control action can happen
            This is to prevent false starts
        '''

        self.sensor_ph = sensor_ph
        self.pump_down = pump_ph_down
        self.pump_up = pump_ph_up

        self.ml_per_s = ml_per_s
        self.dispense_volume = dispense_volume
        self.output_file = output_file

        self.ph_min = ph_min
        self.ph_max = ph_max
        self.control_every = control_every
        self.warmup_time = warmup_time
        self.verbose = verbose

        self.dispense_time = self.dispense_volume / self.ml_per_s

        # write the headers to the output file
        os.makedirs(os.path.dirname(self.output_file),exist_ok=True)
        with open(self.output_file,'a') as fp:
            fp.write("time,datetime,datetime_timezone,ph_down_time,ph_down_volume,ph_up_time,ph_up_volume\n")        


        # Because the test for control is current_time - control_every  < last_control,
        #   Need to subtract control_every here, otherwise it will wait warmup_time + control_every
        #   before it starts to control
        self.last_control = time.time() + self.warmup_time - self.control_every

    def __call__(self):
        '''
        Execute a control command based on the current sensor_ph value, and time since last control
        ''' 
        current_time = time.time()
        if current_time - self.control_every < self.last_control:
            return 

        ph_up_dispensed_volume = 0.
        ph_up_dispensed_time = 0.
        ph_down_dispensed_volume = 0.
        ph_down_dispensed_time = 0.
        
        if self.sensor_ph.ph_avg > self.ph_max:
            if self.verbose:
                print("ph low {:.1f}s since last control".format(current_time-self.last_control))
            self.pump_down(self.dispense_time)
            self.last_control = current_time

            ph_down_dispensed_volume = self.dispense_volume
            ph_down_dispensed_time = self.dispense_time
        elif self.sensor_ph.ph_avg < self.ph_min:
            if self.verbose:
                print("ph high {:.1f}s since last control".format(current_time-self.last_control))
            self.pump_up(self.dispense_time)
            self.last_control = current_time

            ph_up_dispensed_volume = self.dispense_volume
            ph_up_dispensed_time = self.dispense_time
                
        #fp.write("time,datetime,datetime_timezone, ph_down_time,ph_down_volume, ph_up_time,ph_up_volume\n")        
        output = "{},{},{},".format(current_time,datetime.datetime.now(),datetime.datetime.now().astimezone())
        output += "{},{},{},{}\n".format(ph_down_dispensed_time,ph_down_dispensed_volume,ph_up_dispensed_time,ph_up_dispensed_volume)
        with open(self.output_file,'a') as fp:
            fp.write(output)

if __name__ == "__main__":
    from control_ph_pump import Controller_ph_Pump
    from sensor_ph import Sensor_ph
    from controllable_pump import Controllable_Pump
    
    sensor_ph = Sensor_ph(output_file="tmp_output_files/ph_{:.0f}".format(time.time()),
                            read_every=1.0,
                            csv="test/test_inputs/sensor_ph_sinewave01_voltage.csv",
                            verbose=True)
    pump_up = Controllable_Pump(0,verbose=True)
    pump_down = Controllable_Pump(0,verbose=True)
    controller = Controller_ph_Pump(sensor_ph,
                                    pump_up,
                                    pump_down,
                                    output_file="tmp_output_files/Controller_ph_Pump_{:.0f}.csv".format(time.time()),
                                    ml_per_s=5.0, # ml/sec
                                    dispense_volume=1.0, # ml
                                    control_every=2,
                                    warmup_time=0.)

    for ii in range(10):
        print()
        sensor_ph()
        controller()
        time.sleep(.5)