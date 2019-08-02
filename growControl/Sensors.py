import time
#import utils
from growControl.utils import CircularBuffer



class Sensor(object):
    '''
    Defines the common components of a sensor. All sensors devices should inherit from this
    '''
    def __init__(self,config,parent):
        '''
        params is a dictionary of parameters to setup a sensor.
        '''

        self.type = config["type"]
        self.name = config['name']
        self.save_every = int(config['save_every_seconds'])
        self.average_over = int(config['average_over_samples'])
        
        self.parent = parent
        self.outfile = parent.outfile

        self.last_save = 0.0
        self.current_value = None

        self.buffer = CircularBuffer(self.average_over)
    
    def _read_sensor(self):
        '''
        This class must be defined for each sensor
        This method must return a numeric value
        '''
        print("The _read_sensor class must be defined in the subclass")
        return None

    def update(self):
        '''
        Read the sensor value and add it to the devices history
        '''
        # read in the sensor value, calculate the moving average, then call save function
        # The save function deals with the timing of the save
        self.buffer.update(self._read_sensor())
        self.current_value = self.buffer.average
        self.save()

        self.parent.ph = self.current_value


    def save(self):
        '''
        Saves the current value to a csv file if the appropriate time has elapsed
        '''

        if time.time() - self.last_save > self.save_every:
            with open(self.outfile,'a') as f:
                f.write("{},{}\n".format(self.name,self.current_value))
            self.last_save = time.time()


class SensorPh(Sensor):
    '''
    Defines a ph sensor
    '''
    def __init__(self,config,parent):

        print("\t\tIn SensorPh.__init__()")

        self.bus_address = config['bus_address']
        self.ads1115_gain =  config['ads1115_gain']
        self.ads1115_data_sample_rate =  config['ads1115_data_sample_rate']
        self.differential_input1 = config['differential_input1']
        self.differential_input2 = config['differential_input2']

        super().__init__(config,parent)

        print("Sensor {} outfile: {}".format(self.name,self.outfile))
        
    def _read_sensor(self):
        '''
        device specific implementation of this sensor
        This overrides Sensor._read_sensor()
        '''

