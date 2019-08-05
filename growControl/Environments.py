'''
Defines the environment classes.
An environment is a pot or zone.
They have children:
    - Sensors   
    - Controls
    - Other environments 

IE a grow room (zone) and a hydroponic tub (pot) are both environments. 
pH sensing/control happens at the pot level. Light control happens at the zone level. An automatic watering system could operate at either

This means that zones need to be aware of their parents and children
'''
from growControl import Sensors
from growControl import Controls
from growControl import utils
from growControl import GrowObject
import time

class Environment(GrowObject.GrowObject):
    '''
    The base class for all environments.
    Defines basics of an environment
    '''

    def __init__(self,config):
        '''

        '''
        # If a control frequency is set then record it, if not set it to None
        if "control_frequency" in config:
            self.control_frequency = float(config["control_frequency"])
        else:
            self.control_frequency = None
        self.last_run_control =  0.

        # Envoronments are not controllable, as they have no control function
        # To control something in an environment, do so by adding a control object as a child
        self.directly_controllable = False
        
        super().__init__(config)

    def run_control(self):
        '''
        Defines the control loop 
        Is to be implemented in each subclass
        Does not return anything
        '''
        print("Need to implement run_control for a subclass of Environment")


        

class Zone(Environment):
    '''
    Defines a zone, which is a specific environment inside of the world.
    A zone may be an entire grow room, or just 1 light on a plant depending on the setup
    '''

    def __init__(self,config):
        print("Creating zone " + config["name"])
        super().__init__(config)


class Pot(Environment):
    '''
    Defines a pot which is a specific growing medium.
    This could be a hydroponic tank, soil pot, or a region of a garden that is all watered together.
    IE a pot is an environment where all of the growing medium properties are constant
    '''
    def __init__(self,config):
        print("\tCreating Pot " + config["name"])
        super().__init__(config)


ImplementedEnvironments = {"Zone":Zone,
                            "Pot":Pot}