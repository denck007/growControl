

from growControl import utils
from growControl import GrowObject

class Control(GrowObject.GrowObject):
    '''
    All control objects (light, temp, ph, etc) inherit from this class
    All instances of Control objects need to have the value "directly_controllable" set in the json file
    '''

    def __init__(self,config):
        '''
        Create and configure a Control object
        '''
        # Some of the control object are directly controllable, others are turned on by other objects
        self.directly_controllable = config["directly_controllable"]

        super().__init__(config)



    def link_devices(self):
        '''
        After all the devices have been created, need to create links between the sensors and controllers
        This method must be implemented for each sub-class
        '''
        print("Link devices must be implemented in subclass for {}".format(self.name))

class ControlPh(Control):
    '''
    Class for controlling how much ph is in a pot
    An instance of this class will search for sensors it needs to control by inside
        of the pot.children that is listed under from
    '''
    def __init__(self,config):
        '''
        '''
        print("creating controlPh object")
        self.SensorPh_name = config["SensorPh_name"]
        self.ControlPh_up_name = config["ControlPh_up_name"]
        self.ControlPh_down_name = config["ControlPh_down_name"]
        self.targetValue = float(config["targetValue"])
        self.targetRange = float(config["targetRange"])
        

        super().__init__(config)

    def link(self,growObjects):
        '''
        Need to get references to the ph sensor, and the 2 pumps that this is controlling

        This needs access to the World.growObjects dict to do the linking
        '''
        self.SensorPh = growObjects[self.SensorPh_name]
        self.ControlPh_up = growObjects[self.ControlPh_up_name]
        self.ControlPh_down = growObjects[self.ControlPh_down_name]

    def update(self):
        pass
    
    def run_controls(self):
        '''

        '''
        print("running controls on ControlPh")

class ControlPeristalticPump(Control):
    '''
    Peristaltic pump controller
    '''
    def __init__(self,config):
        '''
        '''
        super().__init__(config)



ImplementedControls = {"ControlPh":ControlPh,"ControlPeristalticPump":ControlPeristalticPump}






