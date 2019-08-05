import time
from growControl import utils
from growControl.utils import CircularBuffer
from growControl import GrowObject

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
        return None

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
        self.differential_input1 = config['differential_input1']
        self.differential_input2 = config['differential_input2']

        super().__init__(config)
        
    def _read_sensor(self):
        '''
        device specific implementation of this sensor
        This overrides Sensor._read_sensor()
        '''
        print("\t\tIn read sensor for {}".format(self.name))
        return 1


ImplementedSensors = {"SensorPh_ADS1115":SensorPh_ADS1115}


