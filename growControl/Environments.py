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

from growControl.Sensors import SensorPh_ADS1115
import time

class Environment:
    '''
    The base class for all environments.
    Defines basics of an environment
    '''

    def __init__(self,config,parent):
        '''

        '''
        self.name = config["name"]
        self.type = config["type"]
        self.parent = parent

        # If a control frequency is set then record it, if not set it to None
        if "control_frequency" in config:
            self.control_frequency = float(config["control_frequency"])
        else:
            self.control_frequency = None
        self.last_run_control =  0.

        self.children = []
        children = config["children"]
        for child in children:
            child_type = children[child]["type"]

            if child_type == "Pot":
                self.children.append(Pot(children[child],self))
            elif child_type == "SensorPh_ADS1115":
                self.children.append(SensorPh_ADS1115(children[child],self))
            else:
                print("Item {} with type {} is not defined in the Environment class".format(children[child]["name"],child_type))

    def run_control(self):
        '''
        Defines the control loop 
        Is to be implemented in each subclass
        Does not return anything
        '''
        print("Need to implement run_control for a subclass of Environment")

    def update(self):
        '''
        Update the state of the system by calling the update() method of all children
            This means that all children must have an update method, even if it does nothing
        Read all sensors then run all controls
        '''
        for child in self.children:
            child.update()
        
        # If the control frequency is set it has been atleast that amount of time, then run the control function
        if self.control_frequency is not None:
            if self.last_run_control + self.control_frequency >= time.time():
                self.run_control()
                self.last_run_control = time.time()

    def report_data(self):
        '''
        Output a dict that can be passed up the chain for outputing the data
        '''
        # get all of the children's data
        data = {}
        for child in self.children:
            data[child.name] = child.report_data()
        
        return data
        

class Zone(Environment):
    '''
    Defines a zone, which is a specific environment inside of the world.
    A zone may be an entire grow room, or just 1 light on a plant depending on the setup
    '''

    def __init__(self,config,parent):
        print("Creating zone " + config["name"])
        super().__init__(config,parent)


class Pot(Environment):
    '''
    Defines a pot which is a specific growing medium.
    This could be a hydroponic tank, soil pot, or a region of a garden that is all watered together.
    IE a pot is an environment where all of the growing medium properties are constant
    '''
    def __init__(self,config,parent):
        print("\tCreating Pot " + config["name"])
        super().__init__(config,parent)

