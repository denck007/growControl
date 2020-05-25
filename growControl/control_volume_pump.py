 
import time
import datetime
import os

class Controller_Volume_Pump:
    ''' 
    Uses to pumps to control the volume of a system
    '''

    def __init__(self,
                sensor_volume,
                pump,
                output_file_path,
                output_file_base,
                ml_per_s=2.0,
                dispense_volume=100.0, #ml
                volume_min=7.0, # gallons
                control_every=30*60,
                warmup_time=10*60,
                verbose=False):
        '''
        Turns on a water pump to add water to the tank based on the readings of a sensor_volume
        
        sensor_volume: The sensor to read ph_avg from to control by
        pump: Instance of Controllable_Pump that is connected to an external water tank
        output_file_path: The directory to save the data to 
        output_file_base: The base of the file name to save data to

        ml_per_s: Float: The number of ml of fluid that are dispensed with each second of pump time
        dispense_volume: Float: The volume in ml to dispense with each control cycle
        volume_min: Float, If the volume on sensor_volume.volume_avg is below this value and it has been control_every seconds 
            since the last control action, activate the pump
        control_every: Float: Minimum number of seconds must pass between each control action
        warmup_time: Float: Minimum number of seconds after the controller is instantiated before a control action can happen
            This is to prevent false starts
        '''

        self.sensor_volume = sensor_volume
        self.pump = pump

        self.ml_per_s = ml_per_s
        self.dispense_volume = dispense_volume
        
        self.output_file_path = output_file_path
        self.output_file_base = output_file_base
        os.makedirs(os.path.dirname(self.output_file_path),exist_ok=True)
        self.update_output_file_path()     


        self.volume_min = volume_min
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
                fp.write("time,datetime_timezone, dispensed_time,dispensed_volume\n")    

    def __call__(self):
        '''
        Execute a control command based on the current sensor_volume value, and time since last control
        ''' 
        current_time = time.time()
        if current_time - self.control_every < self.last_loop_time:
            return 

        self.update_output_file_path() # Starts a new output file every day
        
        # Want to only TRY and control every control_every. Updating the time will prevent the next
            #   iteration from trying to run the control again.
        self.last_loop_time = current_time

        dispensed_volume = 0.
        dispensed_time = 0.

        t = datetime.datetime.strftime(datetime.datetime.now(),"%m/%d %H:%M:%S")
        if self.sensor_volume.volume_avg < self.volume_min:
            if self.verbose:
                print("{}: Volume low {:.1f}s since last control".format(t,current_time-self.last_loop_time))
            self.pump(self.dispense_time)
            self.last_action_time = current_time
            self.last_action = "Add Water"
            dispensed_volume = self.dispense_volume
            dispensed_time = self.dispense_time

            #fp.write("time,datetime,datetime_timezone, dispensed_time,dispensed_volume\n")        
            output = "{},{},".format(current_time,datetime.datetime.now().astimezone())
            output += "{},{}\n".format(dispensed_time,dispensed_volume)
            with open(self.output_file,'a') as fp:
                fp.write(output)

if __name__ == "__main__":
    from growControl import Controller_Volume_Pump
    from growControl import Sensor_volume
    from growControl import Controllable_Pump
    
    sensor_volume = Sensor_volume(output_file_path="tmp_output_files/",
                            output_file_base="sensor_volume",
                            calibration_file="test/test_inputs/sensor_volume_calibration_mock.json",
                            calibrate_on_startup=False,
                            read_every=1.0,
                            csv="test/test_inputs/sensor_volume_data_to_calibrate.csv",
                            verbose=True)

    pump = Controllable_Pump(None,verbose=True)
    controller = Controller_Volume_Pump(sensor_volume,
                                    pump,
                                    output_file_path="tmp_output_files/",
                                    output_file_base="controller_ph_pump",
                                    ml_per_s=5.0, # ml/sec
                                    dispense_volume=1.0, # ml
                                    volume_min=2,
                                    control_every=1,
                                    warmup_time=0.)

    for ii in range(10):
        print()
        sensor_volume()
        controller()
        time.sleep(2)
