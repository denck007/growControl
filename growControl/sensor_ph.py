
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
    

    def __init__(self,output_file,average_factor=0.9,read_every=30.,csv=None,calibration_file=None,verbose=False):
        '''
        Create the instance of the ph sensor
         
        If use_csv is not None then it must be a valid file path. This is only for debugging
            the csv file is a file with rows of a single float which is a voltage corresponding to a ph value
                it should be the same as what data_stream.voltage would return
        '''
        self.verbose = verbose

        self.output_file = output_file
        os.makedirs(os.path.dirname(self.output_file),exist_ok=True)
        with open(self.output_file,'a') as fp:
            fp.write("time,datetime,datetime_timezone,voltage_raw,voltage_avg,ph_raw,ph_avg\n")        

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

        self.last_reading = time.time() - self.read_every - 1 # make it so imediatly the data is out of date to force reading

        self.voltage_avg = 0. # the average voltage value, initalize to 0.0 volts which is 7.0 ph
        self.ph_avg = 7.0 # the averaged ph value, set to neutral ph

        self._load_calibration_params(calibration_file)

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
        
        data["4ph_mean"] = sum(data["4ph_raw"])/len(data["4ph_raw"])
        data["7ph_mean"] = sum(data["7ph_raw"])/len(data["7ph_raw"])

        data["m"] = (4.01-7.04)/(data["4ph_mean"]-data["7ph_mean"])
        data["b"]  = 7.04 - data["m"] *data["7ph_mean"]

        calibration_path = os.path.dirname(os.path.abspath(self.output_file))
        with open(os.path.join(calibration_path,'sensor_ph_calibration_raw_'+datetime.datetime.now().isoformat()+".json"),'w') as fp:
            json.dump(data,fp,indent=2)

    def __call__(self):
        '''
        Get a reading from the sensor
        '''
        current_time = time.time()
        if current_time - self.read_every < self.last_reading:
            # not enough time has passed since last reading, just return
            return
    
        voltage = self._read()
        if voltage is None:
            ph = None
        else:
            ph = self.convert_voltage_to_ph(voltage)
            self.last_reading = current_time # Only change if a valid voltage is read
        
        # If there was an error reading voltage is none. 
        #   In this case we do not want to update the moving average
        if voltage is not None: 
            self.voltage_avg = self.voltage_avg * self.average_factor + voltage * (1-self.average_factor)
            self.ph_avg = self.ph_avg * self.average_factor + ph * (1-self.average_factor)

        #fp.write("time,datetime,datetime_timezone,voltage_raw,voltage_avg,ph_raw,ph_avg\n")
        output = "{},{},{},".format(time.time(),datetime.datetime.now(),datetime.datetime.now().astimezone())
        output += "{},{},{},{}\n".format(voltage,self.voltage_avg,ph,self.ph_avg)
        with open(self.output_file,'a') as fp:
            fp.write(output)

        if self.verbose:
            if type(ph) is float:
                print("{:.4f}: ph {:.2f}".format(time.time(),ph))
            else:
                print("{:.4f}: ph {}".format(time.time(),ph))
        return ph

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
