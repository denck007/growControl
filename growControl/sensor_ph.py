
import datetime
import os
import sys
import time

class Sensor_ph:
    '''
    Defines a ph sensor and interface
    '''
    

    def __init__(self,output_file,average_factor=0.9,read_every=30.,csv=None,verbose=False):
        '''
        Create the instance of the ph sensor
         
        If use_csv is not None then it must be a valid file path. This is only for debugging
            the csv file is a file with rows of a single float which is a voltage corresponding to a ph value
                it should be the same as what data_stream.voltage would return
        '''
        self.verbose = verbose

        self.output_file = output_file#"/home/neil/growControl/output_files/ph_sensor.csv"
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

        self._set_calibration_params()

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
        import board
        import busio
        import adafruit_ads1x15.ads1115 as ADS
        from adafruit_ads1x15.analog_in import AnalogIn
        from adafruit_ads1x15.ads1x15 import Mode
        
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
        self.ads1115.mode = Mode.CONTINIOUS
        self.ads1115.data_rate = self.ads1115_data_sample_rate # datarates in samples/secs:8,16,32,64,128,250,475,860

        self.data_stream = AnalogIn(self.ads1115,self.ads1115_single_ended_input_pin)
        self._read = self._read_sensor
    
    def _read_sensor(self):
        '''
        Read the value from the real sensor
        '''
        try:
            value = self.data_stream.voltage()
        except:
            e = sys.exc_info()
            print("Exception thrown while reading ph probe:")
            print("{}: {}".format(e[0],e[1]))
            value = None
        return value

    def _set_calibration_params(self):
        '''
        Set the calibration parameters from a file
        '''
        self.calibration_value_m = 1/0.057 # volts per ph unit
        self.calibration_value_b = 7. # volts of bias in ph unit

    def convert_voltage_to_ph(self,voltage):
        '''
        Using the calibration values convert the voltage to a ph value
        '''
        return self.calibration_value_m * voltage + self.calibration_value_b

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
            print("{:.4f}: ph {:.2f}".format(time.time(),ph))
        return ph

if __name__ == "__main__":
    s = Sensor_ph(output_file="tmp_output_files/ph_{:.0f}.csv".format(time.time()),
                    read_every=1.0,
                    csv="test/test_inputs/sensor_ph_sinewave01_voltage.csv",
                    verbose=True)

    for ii in range(20):
        s()
        time.sleep(.5)