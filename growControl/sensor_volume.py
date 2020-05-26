
import datetime
import os
import sys
import time
import json

try:
    import RPi.GPIO as GPIO
except:
    print("Sensor_ph: Unable to import raspberry pi specific modules" +\
           "\tWill only be able to run in csv mode!")
        
class Sensor_volume:
    '''
    Defines a sensor for measuring the volume in the tank.
    Uses a ultrasonic distance device to measure the top of the water
    The depth is calibrated to the water volume
    '''

    def __init__(self,
                  output_file_path,
                  output_file_base, 
                  trigger_pin=None,
                  echo_pin=None,
                  iterations_per_reading=5,
                  average_factor=0.9,
                  read_every=30.,
                  csv=None,
                  calibration_file=None,
                  calibrate_on_startup=True,
                  verbose=False):
        '''
        Create the instance of the ph sensor
        
        output_file_path: path to where the output data should be saved
        output_file_base: start of the output file name. This will get the date appended to it
        trigger_pin: int - the pin to use to trigger the sensor
        echo_pin: int - the pin to recieve the echo on.
        iterations_per_reading: int, Take this many sensor readings and average them together to get the actual reading
        average_factor: float (0,1), the weighting factor for the exponential moving average calculation
        read_every: float > 0, Minimum number of seconds between each reading
        csv: None or path ot csv file to use as a mock input.
                If csv is not None then it must be a valid file path. This is only for debugging
                    the csv file is a file with rows of a single float which is a time reading from the sensor
                    it should be the time of the pulse duration from the echo response
        calibration_file: None or path to json file with calibration data. 
                            The file must contain keys for 'm' (slope) and 'b' (y-intercept)
                            volume = m*pulse_duration + b
        calibrate_on_startup: Boolean, As for calibration to be done when the object is created
        verbose: Boolean, Output the data to standard out
        '''
        self.verbose = verbose
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        self.iterations_per_reading = iterations_per_reading

        self.output_file_path = output_file_path
        self.output_file_base = output_file_base
        os.makedirs(os.path.dirname(self.output_file_path),exist_ok=True)
        self.update_output_file_path()     

        # how much of the previous value to keep result = previous * average_factor + new * (1-average_factor)
        #   A larger value makes it slower to respond but is more noise resistant
        self.average_factor = average_factor
        self.read_every = read_every # seconds, minimum time between readings

        ####
        # Intialzie everything
        ####

        # allow us to use a csv file instead of the sensor for debugging
        if csv is None:
            self._initialize_sr04()
        elif (csv is None) and (self.trigger_pin is None or self.echo_pin is None):
            raise ValueError("No trigger or echo pin was given, and no testing csv given. This means there is no valid input.")
        else: # debugging
            self._initialize_csv(csv)
        
        if calibrate_on_startup:
            self.calibrate()
        else:
            self._load_calibration_params(calibration_file)

        self.last_reading = time.time() - self.read_every - 1 # make it so imediatly the data is out of date to force reading

        self.pulse_duration_raw = None # initilize the value of the current pulse measurement
        self.pulse_duration_avg = 0. # the average pulse time value, initalize to 0.0
        self.volume_raw = None # initialize the water volume value
        self.volume_avg = 0.0 # the averaged water volume is set to 0.0

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
                fp.write("time,datetime_timezone,pulse_duration_raw,pulse_duration_avg,volume_raw,volume_avg\n")

    def _initialize_csv(self,csv):
        '''
        Read in all the data from the csv file, set up self to read from csv instead of sensor
        csv: path to valid csv file with mock readings
        '''
        with open(csv,'r') as fp:
            data = fp.readlines()
        data = [line.strip("\n") for line in data]
        self.csv_data = [item if item=="None" else float(item) for item in data]
        self.csv_current_position = 0
        self._read = self._read_csv
    
    def _read_csv(self):
        '''
        Return the next value from a csv
        This lets us test without needing the sensor hooked up
        '''
        counts = 0
        sums = 0
        for _ in range(self.iterations_per_reading):
            try:
                value = self.csv_data[self.csv_current_position]
                self.csv_current_position += 1
                sums += value
                counts += 1
            except:
                continue
        if counts == 0:
            return None
        return sums/counts
        
    def _initialize_sr04(self):
        '''
        Initialize the sensor
        '''
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.trigger_pin,GPIO.OUT)
        GPIO.setup(self.echo_pin,GPIO.IN)

        # Set low, then allow to settle
        GPIO.output(self.trigger_pin,False)

        self._read = self._read_sensor
    
    def _read_sensor(self):
        '''
        Read the sensor self.iterations_per_reading times and return the average value
        
        Returns the duration of the pulse for the distance measurement

        Sets the trigger pin high for 10micro seconds
        Then times the duration of the response
        Repeats this self.iterations_per_reading times
        '''
        counts = 0
        sums = 0
        for _ in range(self.iterations_per_reading):
            try:
                # Send out signal
                GPIO.output(self.trigger_pin,True)
                time.sleep(.00001)
                GPIO.output(self.trigger_pin,False)

                # Find the start of the response
                error_timeout = time.time() + 0.1
                while GPIO.input(self.echo_pin) == 0:
                    pulse_start = time.time()
                    if pusle_start > error_timeout:
                        raise ValueError("Timeout while searching for pulse start on volume sensor")
                # Find the end of the response
                error_timeout = time.time() + 0.1
                while GPIO.input(self.echo_pin) == 1:
                    pulse_end = time.time()
                    if pusle_end > error_timeout:
                        raise ValueError("Timeout while searching for pulse end on volume sensor")

                value = pulse_end - pulse_start
                sums += value
                counts += 1

            except:
                e = sys.exc_info()
                print("Exception thrown while reading SR04 Ultrasonic Distance Sensor:")
                print("{}: {}".format(e[0],e[1]))
                value = None
        if counts == 0:
            return None
        else:
            return sums/counts

    def _load_calibration_params(self,calibration_file=None):
        '''
        Set the calibration parameters from a file
        If the file does not exist prompt to calibrate
        '''
        if calibration_file is None:
            # no calibration data was was given, so try and find the file in the output directory
            calibration_path = os.path.dirname(os.path.abspath(self.output_file))
            print(calibration_path)
            calibration_files = [fname for fname in os.listdir(calibration_path) if "{}_calibration_".format(self.__class__.__name__.lower()) in fname]
            if len(calibration_files) == 0:
                print("No calibration data found for class {}, please calibrate now".format(self.__class__.__name__))
                self.calibrate()
                self._load_calibration_params()
                return
            calibration_file = sorted(calibration_files)[-1]
            calibration_file = os.path.join(calibration_path,calibration_file)

        print("Loading calibration data from {}".format(calibration_file))
        with open(calibration_file,'r') as fp:
            data = json.load(fp)
        
        if (data["m"] is None) or (data["b"] is None):
            self.calibrate()
            self._load_calibration_params()
        self.calibration_value_m = float(data["m"])
        self.calibration_value_b = float(data["b"])
        print("Successfully loaded calibration data!")

    def convert_pulse_duration_to_volume(self,pulse_duration):
        '''
        Using the calibration values convert the pulse duration to a volume measurement
        '''
        return self.calibration_value_m * pulse_duration + self.calibration_value_b

    def calibrate(self):
        '''
        Perform a calibration routine on the sensor
        Asks user to add in water, and record the volume that they added.

        It will record:
            * Raw and calculated values to a file called 'sensor_volume_calibration_<timestamp>'
        '''
        calibrate = input("Calibrate Volume Sensor? If no, will load most recent calibration data <y/n>\n")
        if calibrate.lower()[0] != "y":
            self._load_calibration_params()
            return

        volume = []
        pulse_durations = [] # list readings time from the sensor
        volume_raw = input("Enter current volume in the tank: ")
        volume.append(float(volume_raw))
        pulse_durations.append(self._read())

        while True:
            volume_raw = input("Enter the volume added since last record (enter nothing to complete): ")
            if volume_raw == "":
                break
            volume.append(volume[-1] + float(volume_raw)) # entered change, recording total accumulated
            pulse_durations.append(self._read())

        data = self._calibration_compute_line(volume,pulse_durations)
        data["volume_raw"] = volume
        data["pulse_durations"] = pulse_durations        

        calibration_file = self._calibration_save_data(data)
        self._load_calibration_params(calibration_file=calibration_file)

    def _calibration_compute_line(self,volume,pulse_durations):
        '''
        Given lists of the accumulated volute and the pulse durations, 
            determine a line that takes in a pulse duration and returns a volume
        '''
        import numpy as np
        ys = np.array(volume,dtype=np.float32)
        xs = np.array(pulse_durations,dtype=np.float32)
        model = np.polyfit(xs,ys,1)
        return {"m": model[0], "b": model[1]}
    
    def _calibration_save_data(self,data):
        '''
        Save the calibration data to disk
        '''
        calibration_filename = os.path.join(self.output_file_path,"{}_calibration_raw_{}.json".format(self.__class__.__name__.lower(),
                                                                                                    datetime.datetime.now().isoformat()))
        with open(calibration_filename,'w') as fp:
            json.dump(data,fp,indent=2)
        return calibration_filename

    def __call__(self):
        '''
        Get a reading from the sensor
        '''
        current_time = time.time()
        if current_time - self.read_every < self.last_reading:
            # not enough time has passed since last reading, just return
            return

        # Take the reading. If None is returned, just exit now. there is no need to update any values
        #    as nothing has changed
        self.pulse_duration_raw = self._read()
        
        if self.pulse_duration_raw is None:
            return
        self.last_reading = current_time
        self.update_output_file_path() # Starts a new output file every day

        self.volume_raw = self.convert_pulse_duration_to_volume(self.pulse_duration_raw)
        self.pulse_duration_avg = self.pulse_duration_avg * self.average_factor + self.pulse_duration_raw * (1-self.average_factor)
        self.volume_avg = self.volume_avg * self.average_factor + self.volume_raw * (1-self.average_factor)
        
        #fp.write("times,datetime_timezone,pulse_duration_raw,pulse_duration_avg,volume_raw,volume_avg\n")
        output = "{},{},".format(time.time(),datetime.datetime.now().astimezone())
        output += "{},{},{},{}\n".format(self.pulse_duration_raw,self.pulse_duration_avg,self.volume_raw,self.volume_avg)
        with open(self.output_file,'a') as fp:
            fp.write(output)

        if self.verbose:
            t = datetime.datetime.strftime(datetime.datetime.now(),"%m/%d %H:%M:%S")
            if type(self.volume_raw) is float:
                print("{}       Volume: Current: {:.2f} Average: {:.2f}".format(t,self.volume_raw,self.volume_avg))
            else:
                print("{}       Volume: Current: {} Average: {:.2f}".format(t,self.volume_raw,self.volume_avg))


if __name__ == "__main__":
    output_path = "/home/pi/growControl/temp_outputs"
    input_csv = "/home/pi/growControl/test/test_inputs/sensor_volume_data_to_calibrate.csv"
    os.makedirs(output_path,exist_ok=True)
    s = Sensor_volume(output_file_path=output_path,
                        output_file_base="sensor_volume", 
                        trigger_pin=None,
                        echo_pin=None,
                        iterations_per_reading=1,
                        average_factor=0.9,
                        read_every=.00001,
                        csv=input_csv,
                        calibration_file=None,
                        calibrate_on_startup=True,
                        verbose=True)

    for ii in range(5):
        s()
        time.sleep(.01)