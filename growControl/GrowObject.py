
from growControl import utils
from growControl.Interface import Interface

import logging
import time

class GrowObject:
    '''
    This is the base class for all objects to be used in the grow control system
    It defines a few basic things that are common to all classes
    '''
    
    # Properties that can be set for every grow object. Not all of them need to be set for every grow object
    # Default values are set here
    time_warmup = 0.
    time_run_every = 0.
    interface_type = None
    interface = None

    def __init__(self,params,parent):
        '''
        Initialize all the common parts of a grow object
        '''
        # name and parent must be set before super is called
        self.name = params["name"]
        self.parent = parent
        # logger_name is configured  so that it is easier to track the source of the message
        # format is '<parent_name>-<self.name>'.
        #   If self.parent is not defined or is None then <parent_name>=<None>, otherwise <parent_name>=self.parent
        #   If self.name is not defined use __name__  (module name) as the name, otherwise use self.name
        logger_name = "{}-{}".format("<None>" if not hasattr(self,"parent") else "<None>" if self.parent is None else self.parent, self.name if hasattr(self,"name") else __name__)
        self.logger = logging.getLogger(logger_name)
        self.logger.info("Initializing object")

        self.__initialize_value__("time_warmup",params,default_value=self.time_warmup,required=False)
        self.__initialize_value__("time_run_every",params,default_value=self.time_run_every,required=False)
        self.__initialize_value__("inferface_type",params,default_value=self.interface_type,required=False)

        if self.interface_type is not None:
            self.interface = Interface(params["interface"],self)

        self.time_previous = time.time()

    def __initialize_value__(self,param_name,params,default_value="NO_DEFAULT_GIVEN",required=False):
        '''
        Initialize the param_name value in self
        param_name: property name to set, is also the key in params
        params: dictionary with all of the parameters
        default_value: a hardcoded default value that is set for each parameter.
                        This can be set to None
        required: boolean, if it is required that a value be given in params
                If True and param_name is not in params, will throw error
        '''
        if param_name in params:
            value = params[param_name]
        elif (not required) and (default_value is not "NO_DEFAULT_GIVEN"):
            self.logger.warning("{} is not in params for {}. Using default value of {}".format(param_name,self.name,default_value))
            value = default_value
        elif (not required) and (default_value is None):
            self.logger.critical("A default value for {} is not provided and the value is not required to be in params. This is a gap in the code and should be corrected - Program closing".format(param_name))
            raise NotImplementedError("A default value for {} is not provided in {}. This is a gap in the code and should be corrected".format(param_name,self.name))
        else:
            self.logger.critical("{} is required but is not in the given parameters - Program closing".format(param_name))
            raise NotImplementedError("{} is required in {} but is not in the given parameters".format(param_name,self.name))
        setattr(self,param_name,value)

    def __call__(self):
        '''
        Call must be implemented for all objects
        '''
        self.logger.warning("__call__() method used on object, but it has not been implemented - Program Continuing")
        #raise NotImplementedError("__call__ is not implemented for GrowObject {} with type {}".format(self.name,type(self)))
    
    def __create_data_dict(self):
        '''
        Create a dict holding the data that will be sent to the server
        '''
        self.logger.warning("__create_data_dict() method used on object, but it has not been implemented - Program Continuing")
        #raise NotImplementedError("__create_data_dict is not implemented for GrowObject {} with type {}".format(self.name,type(self)))

