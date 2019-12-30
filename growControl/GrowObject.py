
from growControl import utils
from growControl.Interface import Interface

import logging
import time

class loggable:
    '''
    Creates an object that has a logging function
    '''
    def __init__(self,params={},parent=None):
        '''

        '''
        if not hasattr(self,"name"):
            raise KeyError("self.name must be defined for any object that inherits from loggable")
        if parent is not None:
            self.parent = parent

        self.__configure_logger(params)

    def __configure_logger(self,params):
        '''
        Configure the logger
        If 'log_dir' is in the params dict, then create the logger output there
        Otherwise, search up parents for the next instance that has 'log_dir' as a parameter
        '''
        if 'log_dir' in params:
            # If log_dir is defined for this instance, then use it
            self.log_dir = params["log_dir"]
        elif hasattr(self,"parent"):
            # otherwise, look up the parents tree for the first object that has log_dir defined
            # If it hits the top of the tree (object has no attribute parent) then raise an error
            parent_to_look_at = self.parent
            while True:
                if hasattr(parent_to_look_at,"log_dir"):
                    self.log_dir = parent_to_look_at.log_dir
                    break
                elif hasattr(parent_to_look_at,"parent"):
                    parent_to_look_at = parent_to_look_at.parent
                else:
                    raise ValueError("log_dir defined for {} or any of its parents!".format(self.name))
        self.logger = logging.getLogger(self.name)
        # Create handlers
        c_handler = logging.StreamHandler()
        f_handler = logging.FileHandler('file.log')
        c_handler.setLevel(logging.WARNING)
        f_handler.setLevel(logging.ERROR)

        # Create formatters and add it to handlers
        c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        c_handler.setFormatter(c_format)
        f_handler.setFormatter(f_format)

        # Add handlers to the logger
        self.logger.addHandler(c_handler)
        self.logger.addHandler(f_handler)


class GrowObject(loggable):
    '''
    This is the base class for all objects to be used in the grow control system
    It defines a few basic things that are common to all classes
    '''

    def __init__(self,params,parent):
        '''
        Initialize all the common parts of a grow object
        '''
        # name and parent must be set before super is called
        self.name = params["name"]
        self.parent = parent
        super().__init__(params,parent)

        self.__initialize_value__("time_warmup",params,default_value=0.,required=False)
        self.__initialize_value__("time_run_every",params,default_value=0.,required=False)
        self.__initialize_value__("inferface_type",params,required=True)

        self.interface = Interface(params["interface_type"],params["interface_params"],self)
        self.time_previous = time.time()

    def __initialize_value__(self,param_name,params,default_value=None,required=False):
        '''
        Initialize the param_name value in self
        param_name: property name to set, is also the key in params
        params: dictionary with all of the parameters
        default_value: a hardcoded default value that is set for each parameter.
                        If this value is None then nothing will be set
        required: boolean, if it is required that a value be given in params
                If True and param_name is not in params, will throw error
        '''
        if param_name in params:
            value = params[param_name]
        elif (not required) and (default_value is not None):
            self.logger.warning("{} is not in params for {}. Using default value of {}".format(param_name,self.name,default_value))
            value = default_value
        elif (not required) and (default_value is None):
            self.logger.critical("A default value for {} is not provided in {}. This is a gap in the code and should be corrected".format(param_name,self.name))
            raise NotImplementedError("A default value for {} is not provided in {}. This is a gap in the code and should be corrected".format(param_name,self.name))
        else:
            self.logger.critical("{} is required in {} but is not in the given parameters".format(param_name,self.name))
            raise NotImplementedError("{} is required in {} but is not in the given parameters".format(param_name,self.name))
        setattr(self,param_name,value)

    def __call__(self):
        '''
        Call must be implemented for all objects
        '''
        raise NotImplementedError("__call__ is not implemented for GrowObject {} with type {}".format(self.name,type(self)))
    
    def __create_data_dict(self):
        '''
        Create a dict holding the data that will be sent to the server
        '''
        raise NotImplementedError("__create_data_dict is not implemented for GrowObject {} with type {}".format(self.name,type(self)))

