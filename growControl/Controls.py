

from growControl import utils
class Control:
    '''
    All control objects (light, temp, ph, etc) inherit from this class
    '''

    def __init__(self,config,parent):
        '''
        Create and configure a Control object
        '''
        self.name = config["name"]
        self.type = config["type"]
        self.parent = parent

        if "children" in config:
            self.children = utils.BuildChildren(config,self)

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
    def __init__(self,config,parent):
        '''
        '''
        super().__init__(config,parent)
        self.SensorPh_name = config["SensorPh_name"]
        self.ControlPh_up_name = config["ControlPh_up_name"]
        self.ControlPh_down_name = config["ControlPh_down_name"]
        self.targetValue = float(config["targetValue"])
        self.targetRange = float(config["targetRange"])

    def link_devices(self):
        '''
        After all the devices have been created, need to create links between the sensors and controllers
        Th
        '''

        self.SensorPh = self.parent.children[self.SensorPh_name]
        self.ControlPh_up = self.parent.children[self.ControlPh_up_name]
        self.ControlPh_down = self.parent.children[self.ControlPh_down_name]



ImplementedControls = {"ControlPh":ControlPh}






