
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
        average_factor: float (0,1), the weighting factor for the exponential moving average calculation
        read_every: float > 0, Minimum number of seconds between each reading
        csv: None or path ot csv file to use as a mock input.
                If csv is not None then it must be a valid file path. This is only for debugging
                    the csv file is a file with rows of a single float which is a time reading from the sensor
                    it should be the time of the pulse duration from the echo response
        calibration_file: None or path to json file with calibration data. The file must contain keys for XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
        calibrate_on_startup: Boolean, As for calibration to be done when the object is created
        verbose: Boolean, Output the data to standard out
        '''
        self.verbose = verbose
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin

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
                fp.write("time,datetime_timezone,time_raw,time_avg,volume_raw,volume_avg\n")

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
        value = self.csv_data[self.csv_current_position]
        if value == "None":
            value = None
        self.csv_current_position += 1
        return value
        
    def _initialize_sr04(self):
        '''
        Initialize the sensor
        '''
        GPIO.setup(self.trigger_pin,GPIO.OUT)
        GPIO.setup(self.echo_pin,GPIO.IN)

        # Set low, then allow to settle
        GPIO.output(self.trigger_pin,False)

        self._read = self._read_sensor
    
    def _read_sensor(self):
        '''
        Read the value from the real sensor
        
        Returns the duration of the pulse for the distance measurement

        Sets the trigger pin high for 10micro seconds
        Then times the duration of the response
        '''
        try:
            # Send out signal
            GPIO.output(self.trigger_pin,True)
            time.sleep(.00001)
            GPIO.output(self.trigger_pin,False)

            # Find the start of the response
            while GPIO.input(self.echo_pin) == 0:
                pulse_start = time.time()
            # Find the end of the response
            while GPIO.input(self.echo_pin) == 1:
                pulse_end = time.time()

            value = pulse_end - pulse_start
            
        except:
            e = sys.exc_info()
            print("Exception thrown while reading SR04 Ultrasonic Distance Sensor:")
            print("{}: {}".format(e[0],e[1]))
            value = None
        return value

    def _load_calibration_params(self,calibration_file=None):
        '''
        Set the calibration parameters from a file
        If the file does not exist prompt to calibrate
        '''

        need to update and define calibration method.
        Think have table with gallons to time measurements, then interpolate to get values.
        The tank walls are not flat and depth/volume is not consistent.

        if calibration_file is None:
            # no calibration data was was given, so try and find the file in the output directory
            calibration_path = os.path.dirname(os.path.abspath(self.output_file))
            print(calibration_path)
            calibration_files = [fname for fname in os.listdir(calibration_path) if "sensor_ph_calibration_" in fname]
            if len(calibration_files) == 0:
                print("No calibration data found, please calibrate now")
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

        #self.calibration_value_m = -1/0.057 # volts per ph unit
        #self.calibration_value_b = 7. # volts of bias in ph unit

    def convert_pulse_duration_to_volume(self,pulse_duration):
        '''
        Using the calibration values convert the pulse duration to a volume measurement
        '''
        return self.calibration_value_m * voltage + self.calibration_value_b

    def calibrate(self):
        '''
        Perform a calibration routine on the sensor
        Will ask user to place in a 4 ph solution, then a 7ph solution
        It will record:
            * Raw and calculated values to a file called 'sensor_ph_calibration_<timestamp>'
        '''
        calibrate = input("Calibrate Sensor? If no, will load most recent calibration data <y/n>\n")
        if calibrate.lower()[0] != "y":
            self._load_calibration_params()
            return

        calibration_time = 15 # seconds
        calibration_sps = 5 # number of samples per second while doing calibration

        data = {"4ph_raw":[],
                "7ph_raw":[],
                "4ph_mean":None,
                "7ph_mean":None,
                "m":None,
                "b":None}

        # Read 4ph solution
        input("Place probe in 4ph solution and press <Enter>...")
        data.update(self._calibration_get_point_data("4ph",duration=calibration_time,sps=calibration_sps))

        input("Place probe in 7ph solution and press <Enter>...")
        data.update(self._calibration_get_point_data("7ph",duration=calibration_time,sps=calibration_sps))

        data.update(self._calibration_compute_line(data))
        
        print("Average reading for 4ph solution is {:.6f} volts".format(data["4ph_mean"]))
        print("Average reading for 7ph solution is {:.6f} volts".format(data["7ph_mean"]))
        print("Calibration results: ph = {:.6f}*reading + {:.6f}".format(data["m"],data["b"]))
        print("\t{:.6f} ph/V == {:.6f} v/ph, ideal is 0.05916 mV/ph".format(data["m"],1/data["m"]))
        print("Ideal sensor params: ph = {:.6f}*reading + {:.6f}".format(-1/.05916,7.0))

        calibration_file = self._calibration_save_data(data)
        self._load_calibration_params(calibration_file=calibration_file)

    def _calibration_get_point_data(self,name,duration=15,sps=5):
        pause_time = 1./float(sps)

        if not (name=="4ph" or name=="7ph"):
            raise ValueError("in _calibrate_point, name must be either '4ph' or '7ph'")
        
        raw_data = []
        end_time = time.time() + duration
        while time.time() < end_time:
            raw_data.append(self._read())
            time.sleep(pause_time)

        mean = sum(raw_data)/len(raw_data)
        data = {"{}_raw".format(name):raw_data,
                "{}_mean".format(name):mean}

        return data        

    def _calibration_compute_line(self,data):
        '''
        Given a dict with keys '4ph_mean' and '7ph_mean', compute the y-intercept and slope 
            to compute ph from the voltate measurement
        '''
        if ('4ph_mean' not in data) or ('7ph_mean' not in data):
            raise ValueError("in _compute_calibration, 'data' must have keys '4ph_mean' and '7ph_mean. Existing keys are: {}".format(list(data.keys())))

        data["m"] = (4.01-7.0)/(data["4ph_mean"]-data["7ph_mean"])
        data["b"]  = 7.04 - data["m"] *data["7ph_mean"]
        return data

    def _calibration_save_data(self,data):
        '''
        Save the calibration data to disk
        '''
        calibration_filename = os.path.join(self.output_file_path,'sensor_ph_calibration_raw_'+datetime.datetime.now().isoformat()+".json")
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

        self.update_output_file_path() # Starts a new output file every day

        self.pulse_duration_raw = self._read()
        if self.pulse_duration_raw is None:
            self.volume_raw = None
        else:
            self.ph_raw = self.convert_pulse_duration_to_volume(self.pulse_duration_raw)
            self.last_reading = current_time # Only change if a valid voltage is read
        
        # If there was an error reading the pulse duration is none. 
        #   In this case we do not want to update the moving average
        if self.pulse_duration_raw is not None: 
            self.pulse_duration_avg = self.pulse_duration_avg * self.average_factor + self.pulse_duration_raw * (1-self.average_factor)
            self.volume_avg = self.volume_avg * self.average_factor + self.volume_raw * (1-self.average_factor)

        #fp.write("time,datetime_timezone,time_raw,time_avg,volume_raw,volume_avg\n")
        output = "{},{},".format(time.time(),datetime.datetime.now().astimezone())
        output += "{},{},{},{}\n".format(self.pulse_duration_raw,self.pulse_duration_avg,self.volume_raw,self.volume_avg)
        with open(self.output_file,'a') as fp:
            fp.write(output)

        if self.verbose:
            t = datetime.datetime.strftime(datetime.datetime.now(),"%m/%d %H:%M:%S")
            if type(self.ph_raw) is float:
                print("{}       Volume: Current: {:.2f} Average: {:.2f}".format(t,self.volume_raw,self.volume_avg))
            else:
                print("{}       Volume: Current: {} Average: {:.2f}".format(t,self.volume_raw,self.volume_avg))
