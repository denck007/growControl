import time
from growControl import utils
from growControl.utils import CircularBuffer
from growControl import GrowObject

import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_ads1x15.ads1x15 import Mode

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

        self.buffer = CircularBuffer(self.average_over)

        # Sensors are not controllable, as they have no control function
        self.directly_controllable = False

        super().__init__(config)

    def _read_sensor(self):
        '''
        This class must be defined for each sensor
        This method updates the internal variable self.value
        '''
        print("The _read_sensor class must be defined in the subclass")
        raise NotImplementedError

    def update(self):
        '''
        Call the sensor device's read value
        Update the rolling average and the self.value variable
        This method must be called constantly to keep the data up to date
        '''
        # read in the sensor value, calculate the moving average, then call save function
        value = self._read_sensor()
        self.buffer.update(value)
        self._value = self.buffer.average

    
    @property
    def value(self):
        '''
        Return the value of the sensor
        This @property is created so that the object requesting this value can get it in a consistent way
        https://www.programiz.com/python-programming/property
        '''
        return self._value

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
        self.ads.mode = Mode.CONTINIOUS
        self.ads.data_rate = self.ads1115_data_sample_rate # datarates in samples/secs:8,16,32,64,128,250,475,860

        self.data_stream = AnalogIn(self.ads,self.single_ended_input_pin)
        
    def _read_sensor(self):
        '''
        device specific implementation of this sensor
        This overrides Sensor._read_sensor()
        
        Just return
        '''
        return self.voltage_to_ph(self.data_stream.voltage)

    def _calibrate(self, V_at_ph4=.1728, V_at_ph7=0):
        '''
        calibrate the sensor based on the voltage readings at ph=4 and ph=7
        '''
        self.V2ph_m = (7-4)/(V_at_ph7-V_at_ph4)
        self.V2ph_b = 7-self.V2ph_m * V_at_ph7

    def voltage_to_ph(self,voltage):
        '''
        Given a voltage, return the ph of the sensor
        '''
        return self.V2ph_m * voltage + self.V2ph_b


ImplementedSensors = {"SensorPh_ADS1115":SensorPh_ADS1115}


