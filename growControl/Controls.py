


class Control:
    '''
    All control objects (light, temp, ph, etc) inherit from this class
    '''

    def __init__(self,config):
        '''
        Create and configure a Control object
        '''
        self.name = config["name"]
        self.type = config["type"]


class ControlPh(Control):
    '''
    Class for controlling how much ph is in a pot
    An instance of this class will search for sensors it needs to control by inside
        of the pot.children that is listed under from
    '''
    def __init__(self,config):
        '''
        '''
        self.SensorPh_name = config["SensorPh_name"]
        self.ControlPh_up_name = config["ControlPh_up_name"]
        self.ControlPh_down_name = config["ControlPh_down_name"]
        self.targetValue = float(config["targetValue"])
        self.targetRange = float(config["targetRange"])

        







