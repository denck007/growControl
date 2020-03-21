
import datetime
import os
import sys
import time
import json

try:
    import board
    import busio
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn
    from adafruit_ads1x15.ads1x15 import Mode
except:
    print("Sensor_ph: Unable to import raspberry pi specific modules" +\
           "\tWill only be able to run in csv mode!")
        

class Sensor_ph:
    '''
    Defines a ph sensor and interface
    '''
    

    def __init__(self,
                  output_file_path,
                  output_file_base, 
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
                    the csv file is a file with rows of a single float which is a voltage corresponding to a ph value
                    it should be the same as what data_stream.voltage would return
        calibration_file: None or path to json file with calibration data. The file must contain keys "m" and "b" with floats corresponding
                            to the slope and y-intercept of the voltage vs ph plot
        calibrate_on_startup: Boolean, As for calibration to be done when the object is created
        verbose: Boolean, Output the data to standard out
        '''
        self.verbose = verbose

        self.output_file_path = output_file_path
        self.output_file_base = output_file_base
        os.makedirs(os.path.dirname(self.output_file_path),exist_ok=True)
        self.update_output_file_path()     

        # how much of the previous value to keep result = previous * average_factor + new * (1-average_factor)
        #   A larger value makes it slower to respond but is more noise resistant
        self.average_factor = average_factor
        self.read_every = read_every # seconds, minimum time between readings

        self.ads1115_gain =  8
        self.ads1115_data_sample_rate =  8
        self.ads1115_single_ended_input_pin = 0
        
        ####
        # Intialzie everything
        ####

        # allow us to use a csv file as voltage input instead of the sensor for debugging
        if csv is None:
            self._initialize_ads1115()
        else: # debugging
            self._initialize_csv(csv)
        
        if calibrate_on_startup:
            self.calibrate()
        else:
            self._load_calibration_params(calibration_file)

        self.last_reading = time.time() - self.read_every - 1 # make it so imediatly the data is out of date to force reading

        self.voltage_raw = None # initilize the value of the current voltage
        self.voltage_avg = 0. # the average voltage value, initalize to 0.0 volts which is 7.0 ph
        self.ph_raw = None # initilize the ph value
        self.ph_avg = 7.0 # the averaged ph value, set to neutral ph

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
                fp.write("time,datetime_timezone,voltage_raw,voltage_avg,ph_raw,ph_avg\n")

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
        
    def _initialize_ads1115(self):
        '''
        Initialize the sensor
        '''
        self.ads1115_i2c = busio.I2C(board.SCL,board.SDA)
        self.ads1115 = ADS.ADS1115(self.ads1115_i2c)
        # Gain for the system: voltage range:
        # 2/3: 6.144V
        #   1: 4.096V
        #   2: 2.048V
        #   4: 1.024V
        #   8: 0.512V
        #  16: 0.256V
        self.ads1115.gain = self.ads1115_gain
        self.ads1115.mode = Mode.CONTINUOUS
        self.ads1115.data_rate = self.ads1115_data_sample_rate # datarates in samples/secs:8,16,32,64,128,250,475,860

        self.data_stream = AnalogIn(self.ads1115,self.ads1115_single_ended_input_pin)
        self._read = self._read_sensor
    
    def _read_sensor(self):
        '''
        Read the value from the real sensor
        '''
        try:
            value = self.data_stream.voltage
        except:
            e = sys.exc_info()
            print("Exception thrown while reading ph probe:")
            print("{}: {}".format(e[0],e[1]))
            value = None
        return value

    def _load_calibration_params(self,calibration_file=None):
        '''
        Set the calibration parameters from a file
        If the file does not exist prompt to calibrate
        '''
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

    def convert_voltage_to_ph(self,voltage):
        '''
        Using the calibration values convert the voltage to a ph value
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
        calibration_pause = 1.0/calibration_sps #  seconds to wait between samples

        data = {"4ph_raw":[],
                "7ph_raw":[],
                "4ph_mean":None,
                "7ph_mean":None,
                "m":None,
                "b":None}

        # Read 4ph solution
        input("Place probe in 4ph solution and press <Enter>...")
        end_time = time.time() + calibration_time
        counter = 0
        print('Reading...',end="")
        while time.time() < end_time:
            counter += 1
            if counter == (calibration_sps//3):
                print(".",end="")
            data["4ph_raw"].append(self._read())
            time.sleep(calibration_pause)
        print("\nFinished reading 4ph solution.")
        data["4ph_mean"] = sum(data["4ph_raw"])/len(data["4ph_raw"])
        print("Average reading for 4ph solution is {:.6f} volts".format(data["4ph_mean"]))

        # Read 7ph solution
        input("Place probe in 7ph solution and press <Enter>...")
        end_time = time.time() + calibration_time
        counter = 0
        print('Reading...',end="")
        while time.time() < end_time:
            counter += 1
            if counter == (calibration_sps//3):
                print(".",end="")
            data["7ph_raw"].append(self._read())
            time.sleep(calibration_pause)
        print("\nFinished reading 7ph solution.")
        data["7ph_mean"] = sum(data["7ph_raw"])/len(data["7ph_raw"])
        print("Average reading for 7ph solution is {:.6f} volts".format(data["7ph_mean"]))

        data["m"] = (4.01-7.0)/(data["4ph_mean"]-data["7ph_mean"])
        data["b"]  = 7.04 - data["m"] *data["7ph_mean"]
        print("Calibration results: ph = {:.6f}*reading + {:.6f}".format(data["m"],data["b"]))
        print("\t{:.6f} ph/V == {:.6f} v/ph, ideal is 0.05916 mV/ph".format(data["m"],1/data["m"]))
        print("Ideal sensor params: ph = {:.6f}*reading + {:.6f}".format(-1/.05916,7.0))

        calibration_path = os.path.dirname(os.path.abspath(self.output_file))
        calibration_file = os.path.join(calibration_path,'sensor_ph_calibration_raw_'+datetime.datetime.now().isoformat()+".json")
        with open(calibration_file,'w') as fp:
            json.dump(data,fp,indent=2)
        self._load_calibration_params(calibration_file=calibration_file)

    def __call__(self):
        '''
        Get a reading from the sensor
        '''
        current_time = time.time()
        if current_time - self.read_every < self.last_reading:
            # not enough time has passed since last reading, just return
            return

        self.update_output_file_path() # Starts a new output file every day

        self.voltage_raw = self._read()
        if self.voltage_raw is None:
            self.ph_raw = None
        else:
            self.ph_raw = self.convert_voltage_to_ph(self.voltage_raw)
            self.last_reading = current_time # Only change if a valid voltage is read
        
        # If there was an error reading voltage is none. 
        #   In this case we do not want to update the moving average
        if self.voltage_raw is not None: 
            self.voltage_avg = self.voltage_avg * self.average_factor + self.voltage_raw * (1-self.average_factor)
            self.ph_avg = self.ph_avg * self.average_factor + self.ph_raw * (1-self.average_factor)

        #fp.write("time,datetime_timezone,voltage_raw,voltage_avg,ph_raw,ph_avg\n")
        output = "{},{},".format(time.time(),datetime.datetime.now().astimezone())
        output += "{},{},{},{}\n".format(self.voltage_raw,self.voltage_avg,self.ph_raw,self.ph_avg)
        with open(self.output_file,'a') as fp:
            fp.write(output)

        if self.verbose:
            t = datetime.datetime.strftime(datetime.datetime.now(),"%m/%d %H:%M:%S")
            if type(self.ph_raw) is float:
                print("{}       ph: Current: {:.2f} Average: {:.2f}".format(t,self.ph_raw,self.ph_avg))
            else:
                print("{}       ph: Current: {} Average: {:.2f}".format(t,self.ph_raw,self.ph_avg))

if __name__ == "__main__":
    s_csv = Sensor_ph(output_file="tmp_output_files/ph_{:.0f}.csv".format(time.time()),
                    read_every=1.0,
                    csv="test/test_inputs/sensor_ph_sinewave01_voltage.csv",
                    calibration_file="test/test_inputs/sensor_ph_calibration_mock.json",
                    verbose=True)
    #s_sensor = Sensor_ph(output_file="tmp_output_files/ph_{:.0f}.csv".format(time.time()),
    #                read_every=1.0,
    #                csv=None,
    #                calibration_file="test/test_inputs/sensor_ph_calibration_mock.json",
    #                verbose=True)

    for ii in range(20):
        s_csv()
        time.sleep(.5)
