import time
from growControl import utils
from growControl.utils import CircularBuffer
from growControl import GrowObject
try:
    import board
    import busio
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn
    from adafruit_ads1x15.ads1x15 import Mode
except:
    print("Could not import board,busio, and adafruit_ads1x15 libraries, must run in debug_from_file mode")

class Sensor(GrowObject.GrowObject):
    '''
    Defines the common components of a sensor. All sensors devices should inherit from this
    '''
    def __init__(self,config):
        '''
        params is a dictionary of parameters to setup a sensor.
        '''
        self.save_every = int(config['save_every_seconds'])
        self.average_over = int(config['average_over_samples'])

        self._value = None

        # The buffer holds the history of the voltages
        # ph values are converted on the fly
        # This allows us to record the raw history if the calibration changes
        self.buffer = CircularBuffer(self.average_over)

        # Sensors are not controllable, as they have no control function
        self.directly_controllable = False

        if "debug_from_file" in config:
            self.debug_from_file = True
            with open(config["debug_from_file"],'r') as f:
                raw_data = [float(x) for x in f.readlines()]
            self.debug_data = CircularBuffer(raw_data)
        else:
            self.debug_from_file = False

        super().__init__(config)

    def _read_sensor(self):
        '''
        This class must be defined for each sensor
        This method updates the internal variable self.value
        '''
        print("The _read_sensor class must be defined in the subclass")
        raise NotImplementedError

    def _conversion_function(self,raw_value):
        '''
        Convert a raw sensor measurement to useable units
        If the subclass does not implement a different function return the raw value
        '''
        return raw_value

    def update(self):
        '''
        Call the sensor device's read value
        Update the rolling average and the self.value variable
        This method must be called constantly to keep the data up to date
        '''
        # read in the sensor value, calculate the moving average, then call save function
        if self.debug_from_file:
            self.buffer.update(self.debug_data.next())
        else:
            raw_value = self._read_sensor()
            self.buffer.update(raw_value)
        self._value = self.buffer.average

        print("ph: {:.2f}".format(self.value))
    
    @property
    def value(self):
        '''
        Return the ph value converted from the current state of the sensor
        This @property is created so that the object requesting this value can get it in a consistent way
        https://www.programiz.com/python-programming/property
        '''
        return self._conversion_function(self._value)

class SensorPh_ADS1115(Sensor):
    '''
    Defines a ph sensor
    Is indended to be a BNC type sensor with 59.7mV/ph unit sensor
    This sensor is expected to be hooked up to an ADS1115 ACD with programable gain.
    Other ADCs will need to 
    '''
    def __init__(self,config):

        print("\t\tIn SensorPh.__init__()")

        self.bus_address = config['bus_address']
        self.ads1115_gain =  config['ads1115_gain']
        self.ads1115_data_sample_rate =  config['ads1115_data_sample_rate']
        self.single_ended_input_pin = config['single_ended_input_pin']
        super().__init__(config)

        # if we are feeding in data from a text file, then do not activate the 
        if not self.debug_from_file:
            self.i2c = busio.I2C(board.SCL,board.SDA)
            self.ads = ADS.ADS1115(self.i2c)
            # Gain for the system: voltage range:
            # 2/3:6.144V
            #   1: 4.096V
            #   2: 2.048V
            #   4: 1.024V
            #   8: 0.512V
            #  16: 0.256V
            self.ads.gain = self.ads1115_gain
            self.ads.mode = Mode.CONTINUOUS
            self.ads.data_rate = self.ads1115_data_sample_rate # datarates in samples/secs:8,16,32,64,128,250,475,860

            self.data_stream = AnalogIn(self.ads,self.single_ended_input_pin)

        # TODO:
        # Add in method to calibrate on the fly, probably needs some kind of access to database/calibration file
        self._calibrate()
        
    def _read_sensor(self):
        '''
        device specific implementation of this sensor
        This overrides Sensor._read_sensor()

        If using debug_from_file this is never reached as the parent class will not call this
        '''
        return self.data_stream.voltage

    def _calibrate(self, V_at_ph4=.1728, V_at_ph7=0):
        '''
        calibrate the sensor based on the voltage readings at ph=4 and ph=7
        '''
        self.V2ph_m = (7-4)/(V_at_ph7-V_at_ph4)
        self.V2ph_b = 7-self.V2ph_m * V_at_ph7

    def _conversion_function(self,voltage):
        '''
        Given a voltage, return the ph of the sensor
        '''
        return self.V2ph_m * voltage + self.V2ph_b

    def report_data(self):
        '''
        Return a dict of a dict with the data to report
        Format:
            {self.name:{"time":time.time(),
                        "voltage_raw:self.buffer.value, # the current measurement
                        "voltage_smooth:self.buffer.average, # The averaged voltage measurement
                        "ph_raw":self.voltage_to_ph(self.buffer.value),
                        "ph_smooth:self.voltage_to_ph(self.buffer.average)
        '''
        data = {self.name:{"time":time.time(),
                        "voltage_raw":self.buffer.value, # the current measurement
                        "voltage_smooth":self.buffer.average, # The averaged voltage measurement
                        "ph_raw":self._conversion_function(self.buffer.value),
                        "ph_smooth":self.value}}
        return data
       


ImplementedGrowObjects = {"SensorPh_ADS1115":SensorPh_ADS1115}

