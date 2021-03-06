 
import time
import datetime
import os

class Controller_ph_Pump:
    ''' 
    Uses to pumps to control the ph of a system
    '''

    def __init__(self,
                sensor_ph,
                pump_ph_up,
                pump_ph_down,
                output_file_path,
                output_file_base,
                ml_per_s=1.0,
                dispense_volume=3.0,
                ph_min=5.8,
                ph_max=6.2,
                control_every=30*60,
                warmup_time=10*60,
                verbose=False):
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
        
        self.output_file_path = output_file_path
        self.output_file_base = output_file_base
        os.makedirs(os.path.dirname(self.output_file_path),exist_ok=True)
        self.update_output_file_path()     


        self.ph_min = ph_min
        self.ph_max = ph_max
        self.control_every = control_every
        self.warmup_time = warmup_time
        self.verbose = verbose

        self.dispense_time = self.dispense_volume / self.ml_per_s

        # Because the test for control is current_time - control_every  < last_loop_time,
        #   Need to subtract control_every here, otherwise it will wait warmup_time + control_every
        #   before it starts to control
        # last_loop is the last time the controller checked for an action
        # last_action is the last time the controller took an action
        self.last_loop_time = time.time() + self.warmup_time - self.control_every
        self.last_action_time = self.last_loop_time 
        self.last_action = "None"

    def update_output_file_path(self):
        '''
        Updates the property self.output_file
        Checks to see if the file <self.output_file_path> + <self.output_file_base> + <date in YYYY-MM-DD format> .csv
            If it does:
                do nothing
            If it does not exist:
                create it and initialize the header
        '''

        date = datetime.date.today().isoformat()
        self.output_file = os.path.join(self.output_file_path,"{}_{}.csv".format(self.output_file_base,date))
        if not os.path.isfile(self.output_file):
            with open(self.output_file,'a') as fp:
                fp.write("time,datetime_timezone,ph_down_time,ph_down_volume,ph_up_time,ph_up_volume\n")        

    def __call__(self):
        '''
        Execute a control command based on the current sensor_ph value, and time since last control
        ''' 
        current_time = time.time()
        if current_time - self.control_every < self.last_loop_time:
            return 

        self.update_output_file_path() # Starts a new output file every day
        
        # Want to only TRY and control every control_every. Updating the time will prevent the next
            #   iteration from trying to run the control again.
        self.last_loop_time = current_time

        ph_up_dispensed_volume = 0.
        ph_up_dispensed_time = 0.
        ph_down_dispensed_volume = 0.
        ph_down_dispensed_time = 0.

        t = datetime.datetime.strftime(datetime.datetime.now(),"%m/%d %H:%M:%S")
        if self.sensor_ph.ph_avg > self.ph_max:
            if self.verbose:
                print("{}: ph low {:.1f}s since last control".format(t,current_time-self.last_loop_time))
            self.pump_down(self.dispense_time)
            self.last_action_time = current_time
            self.last_action = "Adjust ph Down"
            ph_down_dispensed_volume = self.dispense_volume
            ph_down_dispensed_time = self.dispense_time
        elif self.sensor_ph.ph_avg < self.ph_min:
            if self.verbose:
                print("{}: ph high {:.1f}s since last control".format(t,current_time-self.last_loop_time))
            self.pump_up(self.dispense_time)
            self.last_action_time = current_time
            self.last_action = "Adjust ph Up"
            ph_up_dispensed_volume = self.dispense_volume
            ph_up_dispensed_time = self.dispense_time
        
        if (ph_up_dispensed_time != 0.) or (ph_down_dispensed_time != 0):
            # Only record when an action was taken
            #fp.write("time,datetime,datetime_timezone, ph_down_time,ph_down_volume, ph_up_time,ph_up_volume\n")        
            output = "{},{},".format(current_time,datetime.datetime.now().astimezone())
            output += "{},{},{},{}\n".format(ph_down_dispensed_time,ph_down_dispensed_volume,ph_up_dispensed_time,ph_up_dispensed_volume)
            with open(self.output_file,'a') as fp:
                fp.write(output)

if __name__ == "__main__":
    from growControl import Controller_ph_Pump, Sensor_ph, Controllable_Pump
    
    sensor_ph = Sensor_ph(output_file_path="tmp_output_files/",
                            output_file_base="sensor_ph",
                            calibration_file="test/test_inputs/sensor_ph_calibration_mock.json",
                            calibrate_on_startup=False,
                            read_every=1.0,
                            csv="test/test_inputs/sensor_ph_sinewave01_voltage.csv",
                            verbose=True)
    pump_up = Controllable_Pump(None,verbose=True)
    pump_down = Controllable_Pump(None,verbose=True)
    controller = Controller_ph_Pump(sensor_ph,
                                    pump_up,
                                    pump_down,
                                    output_file_path="tmp_output_files/",
                                    output_file_base="controller_ph_pump",
                                    ml_per_s=5.0, # ml/sec
                                    dispense_volume=1.0, # ml
                                    control_every=2,
                                    warmup_time=0.)

    for ii in range(10):
        print()
        sensor_ph()
        controller()
        time.sleep(.5)
