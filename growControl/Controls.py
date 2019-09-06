

#from growControl import utils
from growControl import GrowObject
import time
try:
    import RPi.GPIO as GPIO
except:
    print("Error importing RPi.GPIO, may need to run with fake data")

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
        if "minimum_time_between_actions" in config:
            self.minimum_time_between_actions = config["minimum_time_between_actions"] # minimum amount of time between performing a control action
        else:
            self.minimum_time_between_actions = 0.0

        if "debug_from_file" in config:
            self.debug_from_file = True
        else:
            self.debug_from_file = False

        # set the time for the first control to be performed in minimum_time_between_actions from initialization
        # This will force the first control to be 2*self.minimum_time_between_actions before first control action
        self.action_last = time.time()+self.minimum_time_between_actions
        
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
        self.mL_per_control = float(config["mL_per_control"])

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
        #print("time: {:.1f} next control time: {:.1f}".format(time.time(),self.action_last+self.minimum_time_between_actions))
        if (time.time() - self.minimum_time_between_actions) < self.action_last:
            # It has not been long enough since last control to run the action again
            #print("In controlPh, it has not been long enough since last control point")
            return
        
        current_pH = self.SensorPh.value
        if current_pH > (self.targetValue + self.targetRange):
            print("{:.1f} ph is {:.2f} which is over the max of {:.2f}+{:.2f}={:.2f}".format(time.time(),current_pH,self.targetValue,self.targetRange,self.targetValue+self.targetRange))
            self.action_last = time.time()
            self.ControlPh_down.run_mL(self.mL_per_control)
        elif current_pH < (self.targetValue - self.targetRange):
            print("{:.1f} ph is {:.2f} which is under the max of {:.2f}-{:.2f}={:.2f}".format(time.time(),current_pH,self.targetValue,self.targetRange,self.targetValue-self.targetRange))
            self.ControlPh_up.run_mL(self.mL_per_control)
            self.action_last = time.time()


class ControlPeristalticPump(Control):
    '''
    Peristaltic pump controller
    '''
    def __init__(self,config):
        '''
        '''
        self.mL_per_second = config["mL_per_second"]
        self.GPIO = int(config["GPIO"])
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.GPIO, GPIO.OUT)
        GPIO.output(self.GPIO,GPIO.HIGH)

        super().__init__(config)

    def run_mL(self,mL_to_dispense):
        '''
        Run the pump for the correct amount of time to dispense mL_to_dispense fluid
        '''
        dispersion_time = mL_to_dispense/self.mL_per_second
        #print("\tSleeping for {:.5f} seconds while dispensing fluid for {}".format(dispersion_time,self.name))
        if self.debug_from_file:
            time.sleep(dispersion_time)
            return

        GPIO.output(self.GPIO,GPIO.LOW)
        
        time.sleep(mL_to_dispense/self.mL_per_second)
        GPIO.output(self.GPIO,GPIO.HIGH)

        report = {self.name:{"time":time.time(),
                             "mL_to_dispense":mL_to_dispense,
                             "dispersion_time":dispersion_time}}
        self.world.data.update(report)



ImplementedGrowObjects = {"ControlPh":ControlPh,"ControlPeristalticPump":ControlPeristalticPump}

