
from growControl import utils
import time

class GrowObject:
    '''
    This is the base class for all objects to be used in the grow control system
    It defines a few basic things that are common to all classes
    '''

    def __init__(self,config):
        self.name = config["name"]
        self.type = config["type"]

    def report_data(self):
        '''
        Output a dict that can be passed up the chain for outputing the data
        '''
        data = {}
        if hasattr(self,'value'):
            data = {"name":self.name,
                    "type":self.type,
                    "value":self.value}
        return data

    def update(self):
        '''
        Update the data in each object
        This method must exist, but does not need to be implemented in each subclass

        This method returns nothing, it purely updates sensor values
        '''
        pass
    
    def link(self,growObjects):
        '''
        Link multiple instances together. This is really useful for Control objects where they run based off of one or more parameters
            of another instance, and they need a reference to the instances they control
        This must be implement on a class by class basis
        '''
        pass

    def run_controls(self):
        '''
        Run the control for an object
        '''
        if self.directly_controllable:
            # If the control frequency is set it has been atleast that amount of time, then run the control function
            if self.control_frequency is not None:
                if self.last_run_control + self.control_frequency >= time.time():
                    self.run_control()
                    self.last_run_control = time.time()
        