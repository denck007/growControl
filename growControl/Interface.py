from growControl.GrowObject import loggable

class Interface(loggable):
    '''
    Defines an interface to IO to read sensors or run controls
    '''
    def __init__(self,interface_type,interface_params,parent):
        '''
        Create an instance of an interface
        '''
        self.name = "{}_interface".format(parent.name)
        self.parent = parent
        super().__init__(parent=parent)

        self.interface_type = interface_type
        self.interface_mode = interface_params["interface_mode"] # either "input" or "output"
        
        if self.interface_type == "GPIO":
            self._config_GPIO(interface_params)
        elif self.interface_type == "SPI":
            self._config_SPI(interface_params)
        elif self.interface_type == "I2C":
            self._config_I2C(interface_params)
        else:
            raise NotImplementedError("interface_type {} is not implemented in growControl.InterfaceType".format(self.interface_type))
    
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

    # These are the functions that the user interfaces with
    def read(self):
        '''
        Read a value from the interface
        '''
        if self.interface_mode != "input":
            raise EnvironmentError("{} is configured as an input, not an output. It is not possible to call read() on an output".format(self.name))
        return self._call_function()

    def write(self,value):
        '''
        Write a value from the interface
        '''
        if self.interface_mode != "output":
            raise EnvironmentError("{} is configured as an output, not an input. It is not possible to call write() on an input".format(self.name))
        return self._call_function(value)
    