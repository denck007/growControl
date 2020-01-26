import logging
#from growControl import GrowObject

class Interface:
    '''
    Defines an interface to IO to read sensors or run controls
    Generic Settings:
        {"interface_type":<GPIO,SPI,I2C,ads1115>,
        "interface_mode":<'input','output'>,
        }
    ADS1115 Settings:
        {"ads1115_gain":<2/3,1,2,4,8,16>,
        "ads1115_data_sample_rate":<8,16,32,64,128,250,475,860>,#samples/second
        "ads1115_single_ended_input_pin":<"P0","P1","P2","P3">
        }
    '''
    def __init__(self,params,parent):
        '''
        Create an instance of an interface
        '''
        assert parent is not None, "All interfaces must have a parent!"
        self.name = "{}_interface".format(parent.name)
        self.parent = parent
        self.logger=logging.getLogger("{}-{}".format(self.parent,self.name))
        self.logger.info("Initializing object")

        self.interface_type = params["interface_type"]
        self.interface_mode = params["interface_mode"] # either "input" or "output"
        
        if self.interface_type == "GPIO":
            self._config_GPIO(params)
        elif self.interface_type == "SPI":
            self._config_SPI(params)
        elif self.interface_type == "I2C":
            self._config_I2C(params)
        elif self.interface_type == "ads1115":
            self._config_ads1115(params)
        elif self.interface_type == "csv":
            self._config_csv(params)
        else:
            self.logger.critical("'interface_type' {} is not implemented - Program closing".format(self.interface_type))
            raise NotImplementedError("interface_type {} is not implemented in growControl.InterfaceType".format(self.interface_type))
    
    # Interface for working with ADS1115
    def _config_ads1115(self,params):
        '''
        Configure an interface for working with the ADS1115 analog to digital converter
        '''
        import board
        import busio
        import adafruit_ads1x15.ads1115 as ADS
        from adafruit_ads1x15.analog_in import AnalogIn
        from adafruit_ads1x15.ads1x15 import Mode

        if self.interface_mode == "input":
            self._call_function = self._read_ads1115
        else:
            self.logger.critical("Device can only be operated in 'input' mode not {} - Program closing".format(self.interface_mode))
            raise KeyError("Invalid interface mode {} in {}".format(self.interface_mode,self.name))

        self.ads1115_gain =  params['ads1115_gain']
        self.ads1115_data_sample_rate =  params['ads1115_data_sample_rate']
        self.ads1115_single_ended_input_pin = params['ads1115_single_ended_input_pin']

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

        raise NotImplementedError("interface_type ADS1115 has not been implemented yet")
    
    def _read_ads1115(self):
        '''
        Read the current value from the ADS1115
        '''
        return self.data_stream.voltage


    def _config_DHT(self,params):
        '''
        Configure reading from a DHT sensor
        These things are really finicy and fail to respond in non-RTOS systems all the time
        '''
        import Adafruit_DHT

        self.interface_mode = "input"
        self._sensor_model = params["sensor_model"]
        self._sensor_pin = params["GPIO_Pin"]
        
        self._retries = params["retries"] if "retries" in params else 10
        self._retry_pauses = params["retry_pause"] if "retry_pause" in params else .1

        if self._sensor_model == "DHT11":
            self._sensor = Adafruit_DHT.DHT11
        elif self._sensor_model == "DHT22":
            self._sensor = Adafruit_DHT.DHT22
        elif self._sensor_model == "AM2302":
            self._sensor = Adafruit_DHT.AM2302
        else:
            raise ValueError("Invalid sensor_model {}. Expected DHT11, DHT22, or AM2302".format(self._sensor_model))
            
        self._call_function = self._read_DHT

    def _read_DHT(self):
        '''
        Read the DHT sensor
        '''
        humidity,temp = Adafruit_DHT.read_retry(self._sensor,
                                                self._sensor_pin,
                                                retries=self._retries,
                                                delay_seconds=self._retry_pauses)
        return (humidity,temp)

    # GPIO interface code
    def _config_GPIO(self,params):
        '''
        Configure an interface for GPIO with params
        '''
        if self.interface_mode == "input":
            self._call_function = self._read_GPIO
        elif self.interface_mode == "output":
            self._call_function = self._write_GPIO
        else:
            self.logger.critical("Invalid interface mode {} - Program closing".format(self.interface_mode))
            raise KeyError("Invalid interface mode {} in {}".format(self.interface_mode,self.name))
        raise NotImplementedError("interface_type GPIO has not been implemented yet")
    
    def _read_GPIO(self):
        '''
        Read the current value of the GPIO 
        '''
        raise NotImplementedError()
    
    def _write_GPIO(self,value):
        '''
        Write value to GPIO
        '''
        raise NotImplementedError()


    # SPI Interface code
    def _config_SPI(self,params):
        '''
        Configure an interface for SPI with params
        '''
        if self.interface_mode == "input":
            self._call_function = self._read_SPI
        elif self.interface_mode == "output":
            self._call_function = self._write_SPI
        else:
            self.logger.critical("Invalid interface mode {} - Program closing".format(self.interface_mode))
            raise KeyError("Invalid interface mode {} in {}".format(self.interface_mode,self.name))
        raise NotImplementedError("interface_type SPI has not been implemented yet")
    
    def _read_SPI(self):
        '''
        Read the current value of the SPI bus 
        '''
        raise NotImplementedError()
    
    def _write_SPI(self,value):
        '''
        Write value to SPI bus
        '''
        raise NotImplementedError()


    # I2C interface code
    def _config_I2C(self,params):
        '''
        Configure an interface for I2C with params
        '''
        if self.interface_mode == "input":
            self._call_function = self._read_I2C
        elif self.interface_mode == "output":
            self._call_function = self._write_I2C
        else:
            self.logger.critical("Invalid interface mode {} - Program closing".format(self.interface_mode))
            raise KeyError("Invalid interface mode {} in {}".format(self.interface_mode,self.name))
        raise NotImplementedError("interface_type I2C has not been implemented yet")
    
    def _read_I2C(self):
        '''
        Read the current value of the I2C bus 
        '''
        raise NotImplementedError()
    
    def _write_I2C(self,value):
        '''
        Write value to I2C bus
        '''
        raise NotImplementedError()

    def _config_csv(self,params):
        '''
        Configure a csv interface 
        Assumes the csv file has 1 row of headers
        '''
        if self.interface_mode == "input":
            self._call_function = self._read_csv
            self._csv_data = None
            self._csv_fname = params["fname"]
            
        elif self.interface_mode == "output":
            self._call_function = self._write_csv
            self._csv_fname = params["fname"]
        else:
            self.logger.critical("Invalid interface mode {} - Program closing".format(self.interface_mode))
            raise KeyError("Invalid interface mode {} in {}".format(self.interface_mode,self.name))

    def _read_csv(self):
        '''
        Read the next line from a csv
        Returns a dict with keys of headers and the values from the current row
        The first time the read method is called it will cache the entire file
        '''
        if self._csv_data is None:
            self._csv_current_line = 0
            with open(self._csv_fname,'r') as fp:
                self._csv_data = fp.readlines()
            self._csv_headers = self._csv_data[0].strip().split(",")
        
        self._csv_current_line += 1
        if len(self._csv_data) >= self._csv_current_line:
            raise EOFError("Requested line past the end of the csv file {}, file only has {} lines, requested line {}".format(self._csv_fname,len(data),self._csv_current_line))
        
        line = {}
        for col_idx,key in enumerate(self._csv_headers):
            line[key] = self._csv_data[self._csv_current_line][col_idx]
        
        return line
    def _write_csv(self,data):
        '''
        Append the data to a csv file
        If data is a string, just dump the string to the csv file
        If data is a list, separate each value with a comma and dump to the file
        '''
        if type(data) is str:
            output = data
        elif type(data) is list:
            output = ""
            for value in data:
                output += "{},".format(value)
            output = output.strip(",")
            output += "\n"
        with open(self._csv_fname,'a') as fp:
            fp.write(output)

    # These are the functions that the user interfaces with
    def read(self):
        '''
        Read a value from the interface
        '''
        if self.interface_mode != "input":
            self.logger.critical("Attempting to call read on interface that is not configured to read - Program closing")
            raise EnvironmentError("{} is configured as an input, not an output. It is not possible to call read() on an output".format(self.name))
        return self._call_function()

    def write(self,value):
        '''
        Write a value from the interface
        '''
        if self.interface_mode != "output":
            self.logger.critical("Attempting to call write on interface that is not configured to write - Program closing")
            raise EnvironmentError("{} is configured as an output, not an input. It is not possible to call write() on an input".format(self.name))
        return self._call_function(value)
    