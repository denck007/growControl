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

from growControl.Sensors import SensorPh

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
        self.outfile = parent.outfile

        self.temperature = None
        self.ph = None
        self.humidity = None
        self.children = []

        children = config["children"]
        for child in children:
            child_type = children[child]["type"]

            if child_type == "Pot":
                self.children.append(Pot(children[child],self))
            elif child_type == "SensorPh":
                self.children.append(SensorPh(children[child],self))

    def run_control(self):
        '''
        Defines the control loop 
        Is to be implemented in each subclass
        Does not return anything
        '''
        print("Need to implement run_control for a subclass of Environment")

    def _save_state(self):
        '''
        Save the state to what ever the output is
        Should only need to be implemented here
        '''
        print("In Environment._save_state()")
        

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

